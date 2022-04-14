import socket
import threading
import time
from json import JSONDecodeError
from sys import exit

from common.decorators import loger
from common.settings import ACTION, PRESENCE, RESPONSE, ERROR, MESSAGE, MESSAGE_TEXT, SENDER, DESTINATION, EXIT
from common.utilites import getting, sending, creating_message, arg_parser
from log import client_log_config

CLIENT_LOGGER = client_log_config.LOGGER


@loger
class Client:
    def __init__(self, address, port, account_name=None):
        self.address = address
        self.port = port
        self.name = account_name
        self.help = 'Доступные команды:\n' \
                    'help - получение справки по командам.\n' \
                    'message - отправить сообщение.\n' \
                    'exit - выход из программы'

    def response(self, message):
        CLIENT_LOGGER.debug(f'Разбор сообщения {message} от сервера')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return 'Соединение установлено'
            return f'Ошибка соединения с сервером: {message[ERROR]}'
        CLIENT_LOGGER.error('Неверный формат сообщения от сервера')
        raise ValueError

    def process(self, transport, name):
        while True:
            try:
                message = getting(transport)
                CLIENT_LOGGER.debug(f'Разбор сообщения {message} от сервера')
                if ACTION in message and message[ACTION] == MESSAGE and SENDER in message \
                        and DESTINATION in message and MESSAGE_TEXT in message \
                        and message[DESTINATION] == name:
                    print(f'Получено сообщение от пользователя '
                          f'{message[SENDER]}:\n{"-" * 50}\n{message[MESSAGE_TEXT]}')
                    CLIENT_LOGGER.info(f'Получено сообщение от пользователя'
                                       f' {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                else:
                    CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, JSONDecodeError):
                CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
                break

    def start(self):
        if not self.name:
            self.name = input('Введите имя пользователя: ')
        try:
            transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            transport.connect((self.address, self.port))
            CLIENT_LOGGER.info(f'Подключение к серверу {self.address}:{self.port}')
            presence_message = creating_message(PRESENCE, transport, self.name)
            sending(transport, presence_message)
            CLIENT_LOGGER.debug('Отправлено приветственное сообщение на сервер')
            answer = self.response(getting(transport))
            print(answer)
            CLIENT_LOGGER.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        except ConnectionRefusedError:
            CLIENT_LOGGER.critical(f'Не удалось подключиться к серверу {self.address}:{self.port},'
                                   f' конечный компьютер отверг запрос на подключение.')
            exit(1)
        except JSONDecodeError:
            CLIENT_LOGGER.error('Ошибка декодирования сообщения.')
            exit(1)
        else:
            sender = threading.Thread(target=self.dialogue_with_user, args=(transport, self.name))
            sender.daemon = True
            sender.start()
            receiver = threading.Thread(target=self.process, args=(transport, self.name))
            receiver.daemon = True
            receiver.start()
            while True:
                time.sleep(1)
                if receiver.is_alive() and sender.is_alive():
                    continue
                break

    def dialogue_with_user(self, sock, user_name):
        print('Добро пожаловать в программу для общения по сети.')
        while True:
            command = input(f'{user_name}, введите команду. Help - вывести список команд:\n ').lower()
            if command == 'help':
                print(self.help)
            elif command == 'message':
                sending(sock, creating_message(MESSAGE, sock, user_name))
            elif command == 'exit':
                sending(sock, creating_message(EXIT, sock, user_name))
                print('Завершение соединения.')
                CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
                time.sleep(0.5)
                break
            else:
                print('Команда не распознана, попробуйте снова.')
                print(self.help)


if __name__ == '__main__':
    attr = arg_parser('client')
    connect_address = attr.address
    connect_port = attr.port
    client = Client(connect_address, connect_port)
    client.start()
