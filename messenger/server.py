import configparser
import os
import sys

import select
import socket
import threading

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox, QApplication

from common.settings import RESPONSE_200, RESPONSE_202, RESPONSE_400, \
    ACTION, PRESENCE, MESSAGE, EXIT, GET_CONTACTS, ADD_CONTACT, REMOVE_CONTACT, USERS_REQUEST, \
    TIME, ACCOUNT_NAME, SENDER, DESTINATION, USER, ERROR, MESSAGE_TEXT, LIST_INFO, DEFAULT_PORT
from common.utilites import getting, sending, arg_parser
from common.decorators import loger
from log import server_log_config
from descriptors import Port
from metaclasses import ServerMaker
from db_creators.server_db import ServerDB
from server_gui import MainWindow, ConfigWindow, gui_create_model, create_stat_model

SERVER_LOGGER = server_log_config.LOGGER

new_connection = False
conflag_lock = threading.Lock()


@loger
class Server(threading.Thread, metaclass=ServerMaker):
    port = Port()

    def __init__(self, address, port, database):
        self.address = address
        self.port = port
        self.database = database
        self.clients = []
        self.messages = []
        self.names = {}
        super().__init__()

    def process(self, message, client):
        global new_connection
        SERVER_LOGGER.debug(f'Разбор сообщения {message} от клиента')
        if ACTION in message and message[ACTION] == PRESENCE \
                and TIME in message and USER in message:
            if message[USER][ACCOUNT_NAME] not in self.names.keys():
                self.names[message[USER][ACCOUNT_NAME]] = client
                client_ip, client_port = client.getpeername()
                self.database.user_login(message[USER][ACCOUNT_NAME], client_ip, client_port)
                sending(client, RESPONSE_200)
                with conflag_lock:
                    new_connection = True
            else:
                response = RESPONSE_400
                response[ERROR] = 'Имя пользователя уже занято.'
                sending(client, response)
                self.clients.remove(client)
                client.close()
            return
        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message \
                and TIME in message and SENDER in message and MESSAGE_TEXT in message \
                and self.names[message[SENDER]] == client:
            if message[DESTINATION] in self.names:
                self.messages.append(message)
                self.database.process_message(message[SENDER], message[DESTINATION])
                sending(client, RESPONSE_200)
            else:
                response = RESPONSE_400
                response[ERROR] = 'Пользователь не зарегистрирован на сервере.'
                sending(client, response)
            return
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            self.database.user_logout(message[ACCOUNT_NAME])
            SERVER_LOGGER.info(f'Клиент {message[ACCOUNT_NAME]} корректно отключился от сервера.')
            self.clients.remove(self.names[message[ACCOUNT_NAME]])
            self.names[message[ACCOUNT_NAME]].close()
            del self.names[message[ACCOUNT_NAME]]
            with conflag_lock:
                new_connection = True
            return
        elif ACTION in message and message[ACTION] == GET_CONTACTS and USER in message \
                and self.names[message[USER]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = self.database.get_contacts(message[USER])
            sending(client, response)
        elif ACTION in message and message[ACTION] == ADD_CONTACT and ACCOUNT_NAME in message \
                and USER in message and self.names[message[USER]] == client:
            self.database.add_contact(message[USER], message[ACCOUNT_NAME])
            sending(client, RESPONSE_200)
        elif ACTION in message and message[ACTION] == REMOVE_CONTACT and ACCOUNT_NAME in message and \
                USER in message and self.names[message[USER]] == client:
            self.database.remove_contact(message[USER], message[ACCOUNT_NAME])
            sending(client, RESPONSE_200)
        elif ACTION in message and message[ACTION] == USERS_REQUEST and ACCOUNT_NAME in message \
                and self.names[message[ACCOUNT_NAME]] == client:
            response = RESPONSE_202
            response[LIST_INFO] = [user[0] for user in self.database.users_list()]
            sending(client, response)
        else:
            response = RESPONSE_400
            response[ERROR] = 'Запрос некорректен.'
            sending(client, response)
            return

    def mailing_of_messages(self, message, listen_socks):
        if message[DESTINATION] in self.names and self.names[message[DESTINATION]] \
                in listen_socks:
            sending(self.names[message[DESTINATION]], message)
            SERVER_LOGGER.info(f'Отправлено сообщение пользователю {message[DESTINATION]}'
                               f' от пользователя {message[SENDER]}.')
        elif message[DESTINATION] in self.names and self.names[message[DESTINATION]] \
                not in listen_socks:
            raise ConnectionError
        else:
            SERVER_LOGGER.error(
                f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
                f'отправка сообщения невозможна.')

    def run(self):
        global new_connection
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
        transport.listen()
        while True:
            try:
                client, client_address = transport.accept()
            except OSError:
                pass
            else:
                SERVER_LOGGER.info(f'Установлено соединение с клиентом {client_address}')
                self.clients.append(client)
            recv_data_lst = []
            send_data_lst = []
            err_lst = []
            try:
                if self.clients:
                    recv_data_lst, send_data_lst, err_lst = select.select(
                        self.clients, self.clients, [], 0)
            except OSError as err:
                SERVER_LOGGER.error(f'Ошибка работы с сокетами: {err}')
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process(getting(client_with_message), client_with_message)
                    except OSError as err:
                        SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()}'
                                           f' отключился от сервера. {err}')
                        for name in self.names:
                            if self.names[name] == client_with_message:
                                self.database.user_logout(name)
                                del self.names[name]
                                break
                        self.clients.remove(client_with_message)
                        with conflag_lock:
                            new_connection = True
            for message in self.messages:
                try:
                    self.mailing_of_messages(message, send_data_lst)
                except (ConnectionAbortedError, ConnectionError,
                        ConnectionResetError, ConnectionRefusedError):
                    SERVER_LOGGER.info(f'Связь с клиентом с именем {message[DESTINATION]}'
                                       f' была потеряна.')
                    self.clients.remove(self.names[message[DESTINATION]])
                    self.database.user_logout(message[DESTINATION])
                    del self.names[message[DESTINATION]]
                    with conflag_lock:
                        new_connection = True
            self.messages.clear()
            if err_lst:
                for client_with_error in err_lst:
                    SERVER_LOGGER.info(f'Клиент {client_with_error.getpeername()}'
                                       f' отключился от сервера.')
                    self.clients.remove(client_with_error)


def config_load():
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


def main():
    config = config_load()
    attr = arg_parser('server', config['SETTINGS']['Default_port'],
                      config['SETTINGS']['Listen_Address'])
    listen_address = attr.address
    listen_port = attr.port
    database = ServerDB(
        os.path.join(config['SETTINGS']['Database_path'],
                     config['SETTINGS']['Database_file']))
    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()
    server_app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.main_ui.statusbarServer.showMessage('Сервер запущен')
    main_window.main_ui.tableViewListClients.setModel(gui_create_model(database))
    main_window.main_ui.tableViewListClients.resizeColumnsToContents()
    main_window.main_ui.tableViewListClients.resizeRowsToContents()
    main_window.main_ui.tableViewStatClients.setModel(create_stat_model(database))
    main_window.main_ui.tableViewStatClients.resizeColumnsToContents()
    main_window.main_ui.tableViewStatClients.resizeRowsToContents()

    def list_update():
        global new_connection
        if new_connection:
            main_window.main_ui.tableViewListClients.setModel(gui_create_model(database))
            main_window.main_ui.tableViewListClients.resizeColumnsToContents()
            main_window.main_ui.tableViewListClients.resizeRowsToContents()
            main_window.main_ui.tableViewStatClients.setModel(create_stat_model(database))
            main_window.main_ui.tableViewStatClients.resizeColumnsToContents()
            main_window.main_ui.tableViewStatClients.resizeRowsToContents()
            with conflag_lock:
                new_connection = False

    def server_config():
        global config_window
        config_window = ConfigWindow()
        config_window.config_ui.lineEditDbPath.insert(config['SETTINGS']['Database_path'])
        config_window.config_ui.lineEditDbFile.insert(config['SETTINGS']['Database_file'])
        config_window.config_ui.lineEditPort.insert(config['SETTINGS']['Default_port'])
        config_window.config_ui.lineEditIP.insert(config['SETTINGS']['Listen_Address'])
        config_window.config_ui.pushButtonSave.clicked.connect(save_server_config)

    def save_server_config():
        global config_window
        message = QMessageBox()
        config['SETTINGS']['Database_path'] = config_window.config_ui.lineEditDbPath.text()
        config['SETTINGS']['Database_file'] = config_window.config_ui.lineEditDbFile.text()
        try:
            port = int(config_window.config_ui.lineEditPort.text())
        except ValueError:
            message.warning(config_window, 'Ошибка', 'Порт должен быть числом')
        else:
            config['SETTINGS']['Listen_Address'] = config_window.config_ui.lineEditIP.text()
            if 1023 < port < 65536:
                config['SETTINGS']['Default_port'] = str(port)
                print(port)
                with open('server.ini', 'w') as conf:
                    config.write(conf)
                    message.information(config_window, 'OK', 'Настройки успешно сохранены!')
            else:
                message.warning(config_window, 'Ошибка', 'Порт должен быть от 1024 до 65536')

    timer = QTimer()
    timer.timeout.connect(list_update)
    timer.start(1000)
    main_window.main_ui.refreshAction.triggered.connect(list_update)
    main_window.main_ui.configAction.triggered.connect(server_config)
    sys.exit(server_app.exec_())


if __name__ == '__main__':
    main()
