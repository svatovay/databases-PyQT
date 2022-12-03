"""
It is a launcher for starting subprocesses for server and clients of two types: senders and listeners.
for more information:
https://stackoverflow.com/questions/67348716/kill-process-do-not-kill-the-subprocess-and-do-not-close-a-terminal-window
"""

import os
import signal
import subprocess
import sys
from time import sleep

PYTHON_PATH = sys.executable
BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def get_subprocess(file_with_args):
    sleep(0.5)
    file_full_path = f"{PYTHON_PATH} {BASE_PATH}/{file_with_args}"
    args = ["gnome-terminal", "--wait", "--", "bash", "-c", file_full_path]
    return subprocess.Popen(args, preexec_fn=os.setpgrp)


def main():
    process = []

    while True:
        action = input(
            'Выберите действие: q - выход , s - запустить сервер, k - запустить клиенты x - закрыть все окна:')
        if action == 'q':
            break
        elif action == 's':
            # Запускаем сервер!
            process.append(get_subprocess("server_main.py"))
        elif action == 'k':
            print('Убедитесь, что на сервере зарегистрировано необходимо количество клиентов с паролем 123456.')
            print('Первый запуск может быть достаточно долгим из-за генерации ключей!')
            clients_count = int(
                input('Введите количество тестовых клиентов для запуска: '))
            # Запускаем клиентов:
            for i in range(1, clients_count + 1):
                process.append(get_subprocess(f"client.py -n test{i} -p 123456"))
        elif action == 'x':
            while process:
                victim = process.pop()
                os.killpg(victim.pid, signal.SIGINT)


if __name__ == '__main__':
    main()
