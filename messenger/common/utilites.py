import argparse
import json
import time
from sys import exit

from common.decorators import log
from common.settings import MAX_PACKAGE_LENGTH, ENCODING, ACTION, PRESENCE, EXIT, TIME, ACCOUNT_NAME, \
    MESSAGE, MESSAGE_TEXT, DEFAULT_PORT, DEFAULT_IP_ADDRESS, SENDER, DESTINATION
from log import client_log_config
from log import server_log_config

CLIENT_LOGGER = client_log_config.LOGGER
SERVER_LOGGER = server_log_config.LOGGER


@log
def getting(client):
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        msg = json.loads(encoded_response.decode(ENCODING))
        if isinstance(msg, dict):
            return msg
        else:
            raise TypeError('Данные должны быть словарем')
    else:
        raise TypeError('Данные должны быть байтами')


@log
def sending(sock, message):
    if isinstance(message, dict):
        encoded_message = json.dumps(message).encode(ENCODING)
    else:
        raise TypeError('Данные должны быть словарем')
    sock.send(encoded_message)


@log
def creating_message(action, sock, account_name):
    message = None
    if action == PRESENCE:
        message = {
            ACTION: action,
            TIME: time.time(),
            ACCOUNT_NAME: account_name
        }
        CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение от пользователя {account_name}')
    elif action == MESSAGE:
        to_user = input('Введите получателя сообщения: ')
        message_text = input('Введите сообщение для отправки или отправьте пустое сообщение'
                             ' для завершения работы: ')
        if not message_text:
            sock.close()
            CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
            exit(0)
        message = {
            ACTION: action,
            SENDER: account_name,
            DESTINATION: to_user,
            TIME: time.time(),
            MESSAGE_TEXT: message_text
        }
        CLIENT_LOGGER.debug(f'Сформировано сообщение : {message} для пользователя {to_user}')
    elif action == EXIT:
        message = {
            ACTION: action,
            TIME: time.time(),
            ACCOUNT_NAME: account_name
        }
    return message


@log
def arg_parser(program):
    parser = argparse.ArgumentParser()
    if program == 'server':
        parser.add_argument('-p', '--port', default=DEFAULT_PORT, type=int,
                            nargs='?', help='Номер порта')
        parser.add_argument('-a', '--address', default=DEFAULT_IP_ADDRESS,
                            type=str, nargs='?', help='IP адрес')
        args = parser.parse_args()
    else:
        parser.add_argument('port', default=DEFAULT_PORT, type=int,
                            nargs='?', help='Номер порта')
        parser.add_argument('address', default=DEFAULT_IP_ADDRESS,
                            type=str, nargs='?', help='IP адрес')
        parser.add_argument('-n', '--name', default=None, type=str,
                            nargs='?', help='Имя пользователя')
        args = parser.parse_args()
        if not 1023 < args.port < 65536:
            CLIENT_LOGGER.error('Порт может быть в диапазоне от 1024 до 65535.')
            exit(1)
    return args
