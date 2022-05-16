import argparse
import json
from sys import exit, path

path.append('../../../client_dist/client/')
from common.decorators import log
from common.settings import MAX_PACKAGE_LENGTH, ENCODING
from log import server_log_config, client_log_config

CLIENT_LOGGER = client_log_config.LOGGER
SERVER_LOGGER = server_log_config.LOGGER


@log
def getting(client):
    """
    Функция приёма сообщений от удалённых компьютеров.
    Принимает сообщения JSON, декодирует полученное сообщение
    и проверяет что получен словарь.
    :param client: socket клиента.
    :return: dict
    """
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
    """
    Функция отправки словарей через сокет.
    Кодирует словарь в формат JSON и отправляет через сокет.
    :param sock: socket клиента.
    :param message: dict
    :return: None
    """
    if isinstance(message, dict):
        encoded_message = json.dumps(message).encode(ENCODING)
    else:
        raise TypeError('Данные должны быть словарем')
    sock.send(encoded_message)


@log
def arg_parser(program, default_port, default_address):
    """
    Функция парсинга аргументов командной строки.
    :param program: str
    :param default_port: int
    :param default_address: str
    :return: argparse.Namespace
    """
    parser = argparse.ArgumentParser()
    args = None
    if program == 'server':
        parser.add_argument('-p', '--port', default=default_port, type=int,
                            nargs='?', help='Номер порта')
        parser.add_argument('-a', '--address', default=default_address,
                            type=str, nargs='?', help='IP адрес')
        parser.add_argument('--no_gui', action='store_true')
        args = parser.parse_args()
    elif program == 'client':
        parser.add_argument('port', default=default_port, type=int,
                            nargs='?', help='Номер порта')
        parser.add_argument('address', default=default_address,
                            type=str, nargs='?', help='IP адрес')
        parser.add_argument('-n', '--name', default=None, type=str,
                            nargs='?', help='Имя пользователя')
        parser.add_argument('-p', '--password', default='', nargs='?')
        args = parser.parse_args()
        if not 1023 < args.port < 65536:
            CLIENT_LOGGER.error('Порт может быть в диапазоне от 1024 до 65535.')
            exit(1)
    return args
