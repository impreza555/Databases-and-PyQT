from log import server_log_config
from sys import exit

SERVER_LOGGER = server_log_config.LOGGER


class Port:
    def __set__(self, instance, value):
        if not 1023 < value < 65536:
            SERVER_LOGGER.critical(f'Неверный номер порта {value}.'
                                   f' Порт может быть в диапазоне от 1024 до 65535.')
            exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
