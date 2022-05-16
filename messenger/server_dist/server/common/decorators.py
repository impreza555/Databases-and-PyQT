import socket
import sys

sys.path.append('../../../client_dist/client/')
from log import client_log_config, server_log_config


def log(func):
    """
    Декоратор, выполняющий логирование вызовов функций.
    Сохраняет события типа debug, содержащие
    информацию об имени вызываемой функции, параметры с которыми
    вызывается функция, и модуль, вызывающий функцию.
    :param func: function
    :return: function
    """
    def log_saver(*args, **kwargs):
        logger = server_log_config.LOGGER if 'server.py' in sys.argv[0] else client_log_config.LOGGER
        res = func(*args, **kwargs)
        logger.debug(f'Была вызвана функция {func.__name__} c параметрами {args}, {kwargs}. '
                     f'Вызов из модуля {func.__module__}.')
        return res

    return log_saver


def loger(cls):
    """
    Декоратор, выполняющий логирование классов,
    проверяет каждый атрибут и метод класса, и применяет
    декоратор @log к методам класса.
    :param cls: class
    :return: class
    """
    class NewClass:
        """
        Класс, применяющий декоратор @log к методам.
        """
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


def login_required(func):
    """
    Декоратор, проверяющий, что клиент авторизован на сервере.
    Проверяет, что передаваемый объект сокета находится в
    списке авторизованных клиентов.
    За исключением передачи словаря-запроса
    на авторизацию. Если клиент не авторизован,
    генерирует исключение TypeError
    :param func: function
    :return: function
    """
    def checker(*args, **kwargs):
        from server.server_main import Server
        from common.settings import ACTION, PRESENCE
        if isinstance(args[0], Server):
            found = False
            for arg in args:
                if isinstance(arg, socket.socket):
                    for client in args[0].names:
                        if args[0].names[client] == arg:
                            found = True
            for arg in args:
                if isinstance(arg, dict):
                    if ACTION in arg and arg[ACTION] == PRESENCE:
                        found = True
            if not found:
                raise TypeError
        return func(*args, **kwargs)
    return checker
