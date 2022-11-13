import sys
import logging
import logging.handlers
import os
from common.variables import LOGGING_LEVEL

sys.path.append('../')

# создаём формировщик логов (formatter):
server_formatter = logging.Formatter('%(asctime)-25s %(levelname)-10s %(filename)-25s %(message)-10s')

# Подготовка имени файла для логирования
path = os.path.dirname(os.path.dirname(__file__))
path = os.path.join(path, 'log_files', 'server.log')

# создаём потоки вывода логов
steam = logging.StreamHandler(sys.stderr)
steam.setFormatter(server_formatter)
steam.setLevel(logging.INFO)
log_file = logging.handlers.TimedRotatingFileHandler(path, encoding='utf8', interval=1, when='D')
log_file.setFormatter(server_formatter)

# создаём регистратор и настраиваем его
logger = logging.getLogger('server_dist')
logger.addHandler(steam)
logger.addHandler(log_file)
logger.setLevel(LOGGING_LEVEL)

# отладка
if __name__ == '__main__':
    logger.critical('Test critical event')
    logger.error('Test error event')
    logger.debug('Test debug event')
    logger.info('Test info event')
