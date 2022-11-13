import sys
import os
import logging
from common.variables import LOGGING_LEVEL

sys.path.append('../')

# создаём формировщик логов (formatter):
client_formatter = logging.Formatter('%(asctime)-25s %(levelname)-10s %(filename)-25s %(message)-10s')

# Подготовка имени файла для логирования
path = os.path.dirname(os.path.dirname(__file__))
path = os.path.join(path, 'log_files', 'client.log')

# создаём потоки вывода логов
steam = logging.StreamHandler(sys.stderr)
steam.setFormatter(client_formatter)
steam.setLevel(logging.INFO)
log_file = logging.FileHandler(path, encoding='utf8')
log_file.setFormatter(client_formatter)

# создаём регистратор и настраиваем его
logger = logging.getLogger('client_dist')
logger.addHandler(steam)
logger.addHandler(log_file)
logger.setLevel(LOGGING_LEVEL)

# отладка
if __name__ == '__main__':
    logger.critical('Test critical event')
    logger.error('Test error event')
    logger.debug('Test debug event')
    logger.info('Test info event')
