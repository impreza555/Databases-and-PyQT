import sys

sys.path.append('../')
from log import client_log_config
from log import server_log_config


def log(func):
    def log_saver(*args, **kwargs):
        logger = server_log_config.LOGGER if 'server.py' in sys.argv[0] else client_log_config.LOGGER
        res = func(*args, **kwargs)
        logger.debug(f'Была вызвана функция {func.__name__} c параметрами {args}, {kwargs}. '
                     f'Вызов из модуля {func.__module__}.')
        return res

    return log_saver


def loger(cls):
    class NewClass:
        def __init__(self, *args, **kwargs):
            self._obj = cls(*args, **kwargs)

        def __getattribute__(self, cls_attr):
            try:
                _ = super().__getattribute__(cls_attr)
            except AttributeError:
                pass
            else:
                return _
            attr = self._obj.__getattribute__(cls_attr)
            if isinstance(attr, type(self.__init__)):
                return log(attr)
            else:
                return attr

    return NewClass
