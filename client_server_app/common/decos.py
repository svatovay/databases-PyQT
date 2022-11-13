import inspect
import logging
import sys

from logs.config import server_log_config, client_log_config
from functools import wraps

sys.path.append('../')


class Log:
    def __init__(self, logger=None):
        self.logger = logger

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            parent_func_name = inspect.currentframe().f_back.f_code.co_name
            module_name = inspect.currentframe().f_back.f_code.co_filename.split("/")[-1]
            if self.logger is None:
                logger_name = module_name.split('.')[0]
                self.logger = logging.getLogger(logger_name)
            self.logger.debug(f'Функция {func.__name__} вызвана из функции {parent_func_name} '
                              f'в модуле {module_name} с аргументами: {args}; {kwargs}', stacklevel=2)
            result = func(*args, **kwargs)
            return result

        return wrapper
