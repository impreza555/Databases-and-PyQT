import binascii
import configparser
import hmac
import os
import sys

import select
import socket
import threading

from json import JSONDecodeError
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

sys.path.append('../')
from common.settings import RESPONSE_200, RESPONSE_202, RESPONSE_400, RESPONSE_511, \
    ACTION, PRESENCE, MESSAGE, EXIT, GET_CONTACTS, ADD_CONTACT, REMOVE_CONTACT, \
    USERS_REQUEST, TIME, ACCOUNT_NAME, SENDER, DESTINATION, \
    USER, ERROR, MESSAGE_TEXT, LIST_INFO, DEFAULT_PORT, MAX_CONNECTIONS, \
    DATA, RESPONSE, PUBLIC_KEY, PUBLIC_KEY_REQUEST, RESPONSE_205
from common.utilites import getting, sending, arg_parser
from common.decorators import loger, log, login_required
from log import server_log_config
from server.descriptors import Port
from server.server_db import ServerDB
from server.server_gui import MainWindow

SERVER_LOGGER = server_log_config.LOGGER


@loger
class Server(threading.Thread):
    """
    Основной класс сервера. Принимает соединения, словари - пакеты
    от клиентов, обрабатывает поступающие сообщения.
    Работает в качестве отдельного потока.
    """
    port = Port()

    def __init__(self, address, port, database):
        """
        Конструктор класса сервера.
        :param address: str - адрес сервера.
        :param port: int - порт сервера.
        :param database: obj - объект базы данных.
        """
        self.address = address
        self.port = port
        self.database = database
        self.sock = None
        self.clients = []
        self.listen_sockets = None
        self.error_sockets = None
        self.running = True
        self.names = {}
        super().__init__()

    @login_required
    def process(self, message, client):
        """
        Метод обработчик поступающих сообщений.
        :param message: json объект сообщения.
        :param client: socket клиента.
        :return: None.
        """
        SERVER_LOGGER.debug(f'Разбор сообщения {message} от клиента')
        if ACTION in message and message[ACTION] == PRESENCE \
                and TIME in message and USER in message:
            self.user_authorization(message, client)
        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message \
                and TIME in message and SENDER in message and MESSAGE_TEXT in message \
                and self.names[message[SENDER]] == client:
            if message[DESTINATION] in self.names:
                self.database.process_message(message[SENDER], message[DESTINATION])
                self.mailing_of_messages(message)
                try:
                    sending(client, RESPONSE_200)
                except OSError:
                    self.remove_client(client)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Пользователь не зарегистрирован на сервере.'
                try:
                    sending(client, response)
                except OSError:
                    pass
            return
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            self.remove_client(client)
        elif ACTION in message and message[ACTION] == GET_CONTACTS and USER in message \
                and self.names[message[USER]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = self.database.get_contacts(message[USER])
            try:
                sending(client, response)
            except OSError:
                self.remove_client(client)
        elif ACTION in message and message[ACTION] == ADD_CONTACT and ACCOUNT_NAME in message \
                and USER in message and self.names[message[USER]] == client:
            self.database.add_contact(message[USER], message[ACCOUNT_NAME])
            try:
                sending(client, RESPONSE_200)
            except OSError:
                self.remove_client(client)
        elif ACTION in message and message[ACTION] == REMOVE_CONTACT and ACCOUNT_NAME in message and \
                USER in message and self.names[message[USER]] == client:
            self.database.remove_contact(message[USER], message[ACCOUNT_NAME])
            try:
                sending(client, RESPONSE_200)
            except OSError:
                self.remove_client(client)
        elif ACTION in message and message[ACTION] == USERS_REQUEST and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = [user[0] for user in self.database.users_list()]
            try:
                sending(client, response)
            except OSError:
                self.remove_client(client)
        elif ACTION in message and message[ACTION] == PUBLIC_KEY_REQUEST and \
                ACCOUNT_NAME in message:
            response = RESPONSE_511
            response[DATA] = self.database.get_pubkey(message[ACCOUNT_NAME])
            if response[DATA]:
                try:
                    sending(client, response)
                except OSError:
                    self.remove_client(client)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Нет публичного ключа для данного пользователя'
                try:
                    sending(client, response)
                except OSError:
                    self.remove_client(client)
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            try:
                sending(client, response)
            except OSError:
                self.remove_client(client)

    def user_authorization(self, message, sock):
        """
        Метод реализующий авторизацию пользователей.
        :param message: json объект.
        :param sock: socket клиента.
        :return: None.
        """
        SERVER_LOGGER.debug(f'Start auth process for {message[USER]}')
        if message[USER][ACCOUNT_NAME] in self.names.keys():
            response = RESPONSE_400
            response[ERROR] = 'Имя пользователя уже занято.'
            try:
                SERVER_LOGGER.debug(f'Имя пользователя занято, отправка {response}')
                sending(sock, response)
            except OSError as err:
                SERVER_LOGGER.debug(f'OS Error {err}')
                pass
            self.clients.remove(sock)
            sock.close()
        elif not self.database.check_user(message[USER][ACCOUNT_NAME]):
            response = RESPONSE_400
            response[ERROR] = 'Пользователь не зарегистрирован.'
            try:
                SERVER_LOGGER.debug(f'Неизвестное имя пользователя, отправка {response}')
                sending(sock, response)
            except OSError:
                pass
            self.clients.remove(sock)
            sock.close()
        else:
            SERVER_LOGGER.debug('Корректное имя пользователя, запуск проверки пароля.')
            message_auth = RESPONSE_511
            random_str = binascii.hexlify(os.urandom(64))
            message_auth[DATA] = random_str.decode('ascii')
            _hash = hmac.new(self.database.get_hash(message[USER][ACCOUNT_NAME]), random_str, 'MD5')
            digest = _hash.digest()
            SERVER_LOGGER.debug(f'Сообщение авторизации = {message_auth}')
            try:
                sending(sock, message_auth)
                ans = getting(sock)
            except OSError as err:
                SERVER_LOGGER.debug('Ошибка авторизации, данные:', exc_info=err)
                sock.close()
                return
            client_digest = binascii.a2b_base64(ans[DATA])
            if RESPONSE in ans and ans[RESPONSE] == 511 and \
                    hmac.compare_digest(digest, client_digest):
                self.names[message[USER][ACCOUNT_NAME]] = sock
                client_ip, client_port = sock.getpeername()
                try:
                    sending(sock, RESPONSE_200)
                except OSError:
                    self.remove_client(message[USER][ACCOUNT_NAME])
                self.database.user_login(
                    message[USER][ACCOUNT_NAME],
                    client_ip,
                    client_port,
                    message[USER][PUBLIC_KEY]
                )
            else:
                response = RESPONSE_400
                response[ERROR] = 'Неверный пароль.'
                try:
                    sending(sock, response)
                except OSError:
                    pass
                self.clients.remove(sock)
                sock.close()

    def remove_client(self, client):
        """
        Метод обработчик клиента с которым прервана связь.
        Ищет клиента и удаляет его из списков и базы:
        :param client: socket клиента.
        :return: None.
        """
        SERVER_LOGGER.info(f'Клиент {client.getpeername()} отключился от сервера.')
        for name in self.names:
            if self.names[name] == client:
                self.database.user_logout(name)
                del self.names[name]
                break
        self.clients.remove(client)
        client.close()

    def mailing_of_messages(self, message):
        """
        Метод отправки сообщения клиенту.
        :param message: json объект.
        :return: None.
        """
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] \
                in self.listen_sockets:
            try:
                sending(self.names[message[DESTINATION]], message)
                SERVER_LOGGER.info(f'Отправлено сообщение пользователю {message[DESTINATION]}'
                                   f' от пользователя {message[SENDER]}.')
            except OSError:
                self.remove_client(message[DESTINATION])
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] \
                not in self.listen_sockets:
            SERVER_LOGGER.error(f'Связь с клиентом {message[DESTINATION]} была потеряна.'
                                f' Соединение закрыто, доставка невозможна.')
            self.remove_client(self.names[message[DESTINATION]])
        else:
            SERVER_LOGGER.error(f'Пользователь {message[DESTINATION]} не зарегистрирован'
                                f' на сервере, отправка сообщения невозможна.')

    def service_update_lists(self):
        """
        Метод реализующий отправки сервисного сообщения 205 клиентам.
        :return: None.
        """
        for client in self.names:
            try:
                sending(self.names[client], RESPONSE_205)
            except OSError:
                self.remove_client(self.names[client])

    def run(self):
        """
        Метод запускает сервер.
        :return: None.
        """
        SERVER_LOGGER.info(f'Запущен сервер. '
                           f'Адрес(а) с которого(ых) принимаются подключения:'
                           f' {"любой" if not self.address else self.address}, '
                           f'Порт для подключений: {self.port}')
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        transport.bind((self.address, self.port))
        transport.settimeout(0.5)
        SERVER_LOGGER.info(f'Сервер начал прослушивание{" всех" if not self.address else ""}'
                           f' адреса(ов) {"," if not self.address else ": " + self.address + ","}'
                           f' Порт для подключений: {self.port}')
        self.sock = transport
        self.sock.listen(MAX_CONNECTIONS)
        while self.running:
            try:
                client, client_address = self.sock.accept()
            except OSError:
                pass
            else:
                SERVER_LOGGER.info(f'Установлено соединение с клиентом {client_address}')
                client.settimeout(5)
                self.clients.append(client)
            recv_data_lst = []
            try:
                if self.clients:
                    recv_data_lst, self.listen_sockets, self.error_sockets = select.select(
                        self.clients, self.clients, [], 0)
            except OSError as err:
                SERVER_LOGGER.error(f'Ошибка работы с сокетами: {err.errno}')
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process(getting(client_with_message), client_with_message)
                    except (OSError, JSONDecodeError, TypeError) as err:
                        SERVER_LOGGER.debug('Получение данных из клиентского исключения.',
                                            exc_info=err)
                        self.remove_client(client_with_message)


@log
def config_load():
    """
    Парсер конфигурационного ini файла.
    :return: object - объект конфигурации.
    """
    config = configparser.ConfigParser()
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f"{dir_path}/{'server.ini'}")
    if 'SETTINGS' in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'Default_port', str(DEFAULT_PORT))
        config.set('SETTINGS', 'Listen_Address', '')
        config.set('SETTINGS', 'Database_path', '')
        config.set('SETTINGS', 'Database_file', 'server_db.db3')
        return config


@log
def main():
    """
    Главная функция программы.
    :return: None.
    """
    config = config_load()
    attr = arg_parser('server', config['SETTINGS']['Default_port'],
                      config['SETTINGS']['Listen_Address'])
    listen_address = attr.address
    listen_port = attr.port
    gui_flag = attr.no_gui
    database = ServerDB(
        os.path.join(config['SETTINGS']['Database_path'],
                     config['SETTINGS']['Database_file']))
    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()
    if gui_flag:
        while True:
            command = input('Введите exit для завершения работы сервера.')
            if command == 'exit':
                server.running = False
                server.join()
                break
    else:
        server_app = QApplication(sys.argv)
        server_app.setAttribute(Qt.AA_DisableWindowContextHelpButton)
        main_window = MainWindow(database, server, config)
        main_window.show()
        server_app.exec_()
        server.running = False


if __name__ == '__main__':
    main()
