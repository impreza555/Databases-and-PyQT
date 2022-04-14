"""Здесь производятся настройки приложения"""
import logging

# Порт по умолчанию для сетевого взаимодействия
DEFAULT_PORT = 7777

# IP адрес по умолчанию для подключения клиента
DEFAULT_IP_ADDRESS = '127.0.0.1'

# Максимальная очередь подключений
MAX_CONNECTIONS = 5

# Максимальная длинна сообщения в байтах
MAX_PACKAGE_LENGTH = 1024

# Кодировка проекта
ENCODING = 'utf-8'

# Текущий уровень логирования
LOGGING_LEVEL = logging.DEBUG

# Протокол JIM основные ключи:
ACTION = 'action'
TIME = 'time'
ACCOUNT_NAME = 'account_name'
SENDER = 'from'
DESTINATION = 'to'

# Прочие ключи, используемые в протоколе
PRESENCE = 'presence'
MESSAGE = 'message'
EXIT = 'exit'
MESSAGE_TEXT = 'message_text'
RESPONSE = 'response'
ERROR = 'error'
