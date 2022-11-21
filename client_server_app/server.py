import dis
import select
import sys
import socket
import argparse
import logging
from logs.config import server_log_config

from common.variables import DEFAULT_PORT, MAX_CONNECTIONS, ACTION, TIME, \
    USER, ACCOUNT_NAME, SENDER, PRESENCE, ERROR, MESSAGE, \
    MESSAGE_TEXT, RESPONSE_400, DESTINATION, RESPONSE_200, EXIT
from common.utils import get_message, send_message
from common.decos import Log


class PortChecker:

    def __get__(self, instance, instance_type):
        return instance.__dict__[self.my_attr]

    def __set__(self, instance, value):
        if not (value >= 0 and isinstance(value, int)):
            raise ValueError("Номер порта должен быть целочиселлным и >= 0")
        instance.__dict__[self.my_attr] = value

    def __set_name__(self, owner, my_attr):
        self.my_attr = my_attr


class ServerVerifier(type):

    def __init__(cls, *args, **kwargs):
        check = False
        for key, value in cls.__dict__.items():
            try:
                ret = dis.get_instructions(value)
            except TypeError:
                pass
            else:
                for i in ret:
                    if i.opname == 'LOAD_METHOD' and i.argval == 'connect':
                        raise Exception('Don`t use socket.accept & socket.listen in a client app')
                    if i.opname == 'LOAD_ATTR' and i.argval == 'SOCK_DGRAM':
                        raise Exception('Don`t use socket.SOCK_DGRAM  to TCP connect')


class Server(metaclass=ServerVerifier):
    listen_port = PortChecker()

    # Инициализация логирования сервера.
    def __init__(self, listen_port):
        self.listen_port = listen_port
        self.LOGGER = logging.getLogger('server_dist')

    def process_client_message(self, message, messages_list, client, clients, names):
        """
        Обработчик сообщений от клиентов, принимает словарь - сообщение от клиента,
        проверяет корректность, отправляет словарь-ответ в случае необходимости.
        :param message:
        :param messages_list:
        :param client:
        :param clients:
        :param names:
        :return:
        """
        self.LOGGER.debug(f'Разбор сообщения от клиента : {message}')
        # Если это сообщение о присутствии, принимаем и отвечаем
        if ACTION in message and message[ACTION] == PRESENCE and \
                TIME in message and USER in message:
            # Если такой пользователь ещё не зарегистрирован,
            # регистрируем, иначе отправляем ответ и завершаем соединение.
            if message[USER][ACCOUNT_NAME] not in names.keys():
                names[message[USER][ACCOUNT_NAME]] = client
                send_message(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято.'
                send_message(client, response)
                clients.remove(client)
                client.close()
            return
        # Если это сообщение, то добавляем его в очередь сообщений.
        # Ответ не требуется.
        elif ACTION in message and message[ACTION] == MESSAGE and \
                DESTINATION in message and TIME in message \
                and SENDER in message and MESSAGE_TEXT in message:
            messages_list.append(message)
            return
        # Если клиент выходит
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            clients.remove(names[message[ACCOUNT_NAME]])
            names[message[ACCOUNT_NAME]].close()
            del names[message[ACCOUNT_NAME]]
            return
        # Иначе отдаём Bad request
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            send_message(client, response)
            return

    def process_message(self, message, names, listen_socks):
        """
        Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение,
        список зарегистрированых пользователей и слушающие сокеты. Ничего не возвращает.
        :param message:
        :param names:
        :param listen_socks:
        :return:
        """
        if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
            send_message(names[message[DESTINATION]], message)
            self.LOGGER.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                             f'от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
            raise ConnectionError
        else:
            self.LOGGER.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
                f'отправка сообщения невозможна.')

    def arg_parser(self):
        """Парсер аргументов коммандной строки"""
        parser = argparse.ArgumentParser()
        parser.add_argument('-p', default=self.listen_port, type=int, nargs='?')
        parser.add_argument('-a', default='', nargs='?')
        namespace = parser.parse_args(sys.argv[1:])
        listen_address = namespace.a
        self.listen_port = namespace.p

        # проверка получения корректного номера порта для работы сервера.
        if not 1023 < self.listen_port < 65536:
            self.LOGGER.critical(
                f'Попытка запуска сервера с указанием неподходящего порта {self.listen_port}. '
                f'Допустимы адреса с 1024 до 65535.')
            sys.exit(1)

        return listen_address, self.listen_port

    def main(self):
        """
        Загрузка параметров командной строки, если нет параметров, то задаём значения по умоланию
        :return:
        """
        listen_address, listen_port = self.arg_parser()

        self.LOGGER.info(
            f'Запущен сервер, порт для подключений: {listen_port}, '
            f'адрес с которого принимаются подключения: {listen_address}. '
            f'Если адрес не указан, принимаются соединения с любых адресов.')
        # Готовим сокет
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        transport.bind((listen_address, listen_port))
        transport.settimeout(0.5)

        # список клиентов , очередь сообщений
        clients = []
        messages = []

        # Словарь, содержащий имена пользователей и соответствующие им сокеты.
        names = dict()  # {client_name: client_socket}

        # Слушаем порт
        transport.listen(MAX_CONNECTIONS)
        # Основной цикл программы сервера
        while True:
            # Ждём подключения, если таймаут вышел, ловим исключение.
            try:
                client, client_address = transport.accept()
            except OSError:
                pass
            else:
                self.LOGGER.info(f'Установлено соедение с ПК {client_address}')
                clients.append(client)

            recv_data_lst = []
            send_data_lst = []
            err_lst = []
            # Проверяем на наличие ждущих клиентов
            try:
                if clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(clients, clients, [], 0)
            except OSError:
                pass

            # принимаем сообщения и если ошибка, исключаем клиента.
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process_client_message(get_message(client_with_message),
                                                    messages, client_with_message, clients, names)
                    except Exception:
                        self.LOGGER.info(f'Клиент {client_with_message.getpeername()} '
                                         f'отключился от сервера.')
                        clients.remove(client_with_message)

            # Если есть сообщения, обрабатываем каждое.
            for i in messages:
                try:
                    self.process_message(i, names, send_data_lst)
                except Exception:
                    self.LOGGER.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
                    clients.remove(names[i[DESTINATION]])
                    del names[i[DESTINATION]]
            messages.clear()


if __name__ == '__main__':
    server = Server(DEFAULT_PORT)
    server.main()
