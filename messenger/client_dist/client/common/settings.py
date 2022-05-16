"""Здесь производятся настройки приложения"""
import logging

# Порт по умолчанию для сетевого взаимодействия
DEFAULT_PORT = 7777

# IP адрес по умолчанию для подключения клиента
DEFAULT_IP_ADDRESS = '127.0.0.1'

# Максимальная очередь подключений
MAX_CONNECTIONS = 5

# Максимальная длинна сообщения в байтах
MAX_PACKAGE_LENGTH = 10240

# Кодировка проекта
ENCODING = 'utf-8'

# Текущий уровень логирования
LOGGING_LEVEL = logging.DEBUG

# База данных для хранения данных сервера:
SERVER_CONFIG = 'server_dist.ini'

# Протокол JIM основные ключи:
ACTION = 'action'
TIME = 'time'
USER = 'user'
ACCOUNT_NAME = 'account_name'
SENDER = 'from'
DESTINATION = 'to'
DATA = 'bin'
PUBLIC_KEY = 'pubkey'

# Прочие ключи, используемые в протоколе
PRESENCE = 'presence'
MESSAGE = 'message'
EXIT = 'exit'
MESSAGE_TEXT = 'message_text'
RESPONSE = 'response'
ERROR = 'error'
GET_CONTACTS = 'get_contacts'
LIST_INFO = 'data_list'
REMOVE_CONTACT = 'remove'
ADD_CONTACT = 'add'
USERS_REQUEST = 'get_users'
PUBLIC_KEY_REQUEST = 'pubkey_need'

# Словари - ответы:
RESPONSE_200 = {RESPONSE: 200}
RESPONSE_202 = {RESPONSE: 202, LIST_INFO: None}
RESPONSE_205 = {RESPONSE: 205}
RESPONSE_400 = {RESPONSE: 400, ERROR: None}
RESPONSE_511 = {RESPONSE: 511, DATA: None}
