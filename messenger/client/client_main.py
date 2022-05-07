import os
import socket
import sys
import time
import threading
from json import JSONDecodeError
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication

sys.path.append('../')
from client_db import ClientDB
from client_gui import StartDialog, ClientMainWindow
from common.decorators import loger
from common.errors import ServerError
from common.settings import PRESENCE, RESPONSE, ERROR, ACTION, MESSAGE, \
    EXIT, ADD_CONTACT, REMOVE_CONTACT, GET_CONTACTS, USERS_REQUEST, MESSAGE_TEXT, \
    LIST_INFO, SENDER, DESTINATION, TIME, ACCOUNT_NAME, USER, DEFAULT_PORT, DEFAULT_IP_ADDRESS
from common.utilites import getting, sending, arg_parser
from log import client_log_config

CLIENT_LOGGER = client_log_config.LOGGER
socket_lock = threading.Lock()


@loger
class ClientTransport(threading.Thread, QObject):
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, port, ip_address, database, username):
        threading.Thread.__init__(self)
        QObject.__init__(self)
        self.database = database
        self.username = username
        self.transport = None
        self.connection_init(port, ip_address)
        try:
            self.user_list_update()
            self.contacts_list_update()
        except OSError as err:
            if err.errno:
                CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
                raise ServerError('Потеряно соединение с сервером!')
            CLIENT_LOGGER.error('Timeout соединения при обновлении списков пользователей.')
        except JSONDecodeError:
            CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
            raise ServerError('Потеряно соединение с сервером!')
        self.running = True

    def connection_init(self, port, ip):
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.transport.settimeout(5)
        connected = False
        for i in range(5):
            CLIENT_LOGGER.info(f'Попытка подключения №{i + 1}')
            try:
                self.transport.connect((ip, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                break
            time.sleep(1)
        if not connected:
            CLIENT_LOGGER.critical('Не удалось установить соединение с сервером')
            raise ServerError('Не удалось установить соединение с сервером')
        CLIENT_LOGGER.debug('Установлено соединение с сервером')
        try:
            with socket_lock:
                sending(self.transport, self.create_presence())
                self.process_server_ans(getting(self.transport))
        except (OSError, JSONDecodeError):
            CLIENT_LOGGER.critical('Потеряно соединение с сервером!')
            raise ServerError('Потеряно соединение с сервером!')
        CLIENT_LOGGER.info('Соединение с сервером успешно установлено.')

    def create_presence(self):
        out = {
            ACTION: PRESENCE,
            TIME: time.time(),
            USER: {
                ACCOUNT_NAME: self.username
            }
        }
        CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {self.username}')
        return out

    def process_server_ans(self, message):
        CLIENT_LOGGER.debug(f'Разбор сообщения от сервера: {message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return
            elif message[RESPONSE] == 400:
                raise ServerError(f'{message[ERROR]}')
            else:
                CLIENT_LOGGER.debug(f'Принят неизвестный код подтверждения {message[RESPONSE]}')
        elif ACTION in message \
                and message[ACTION] == MESSAGE \
                and SENDER in message \
                and DESTINATION in message \
                and MESSAGE_TEXT in message \
                and message[DESTINATION] == self.username:
            CLIENT_LOGGER.debug(f'Получено сообщение от пользователя {message[SENDER]} '
                                f'{message[MESSAGE_TEXT]}')
            self.database.save_message(message[SENDER], 'in', message[MESSAGE_TEXT])
            self.new_message.emit(message[SENDER])

    def contacts_list_update(self):
        CLIENT_LOGGER.debug(f'Запрос контакт листа для пользователя {self.name}')
        req = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            USER: self.username
        }
        CLIENT_LOGGER.debug(f'Сформирован запрос {req}')
        with socket_lock:
            sending(self.transport, req)
            ans = getting(self.transport)
        CLIENT_LOGGER.debug(f'Получен ответ {ans}')
        if RESPONSE in ans and ans[RESPONSE] == 202:
            for contact in ans[LIST_INFO]:
                self.database.add_contact(contact)
        else:
            CLIENT_LOGGER.error('Не удалось обновить список контактов.')

    def user_list_update(self):
        CLIENT_LOGGER.debug(f'Запрос списка известных пользователей {self.username}')
        req = {
            ACTION: USERS_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            sending(self.transport, req)
            ans = getting(self.transport)
        if RESPONSE in ans and ans[RESPONSE] == 202:
            self.database.add_users(ans[LIST_INFO])
        else:
            CLIENT_LOGGER.error('Не удалось обновить список известных пользователей.')

    def add_contact(self, contact):
        CLIENT_LOGGER.debug(f'Создание контакта {contact}')
        req = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            sending(self.transport, req)
            self.process_server_ans(getting(self.transport))

    def remove_contact(self, contact):
        CLIENT_LOGGER.debug(f'Удаление контакта {contact}')
        req = {
            ACTION: REMOVE_CONTACT,
            TIME: time.time(),
            USER: self.username,
            ACCOUNT_NAME: contact
        }
        with socket_lock:
            sending(self.transport, req)
            self.process_server_ans(getting(self.transport))

    def transport_shutdown(self):
        self.running = False
        message = {
            ACTION: EXIT,
            TIME: time.time(),
            ACCOUNT_NAME: self.username
        }
        with socket_lock:
            try:
                sending(self.transport, message)
            except OSError:
                pass
        CLIENT_LOGGER.debug('Транспорт завершает работу.')
        time.sleep(0.5)

    def send_message(self, to, message):
        message_dict = {
            ACTION: MESSAGE,
            SENDER: self.username,
            DESTINATION: to,
            TIME: time.time(),
            MESSAGE_TEXT: message
        }
        CLIENT_LOGGER.debug(f'Сформирован словарь сообщения: {message_dict}')
        with socket_lock:
            sending(self.transport, message_dict)
            self.process_server_ans(getting(self.transport))
            CLIENT_LOGGER.info(f'Отправлено сообщение для пользователя {to}')

    def run(self):
        CLIENT_LOGGER.debug('Запущен процесс - приёмник сообщений с сервера.')
        while self.running:
            time.sleep(1)
            with socket_lock:
                try:
                    self.transport.settimeout(0.5)
                    message = getting(self.transport)
                except OSError as err:
                    if err.errno:
                        CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
                        self.running = False
                        self.connection_lost.emit()
                except (ConnectionError, ConnectionAbortedError,
                        ConnectionResetError, JSONDecodeError, TypeError):
                    CLIENT_LOGGER.debug('Потеряно соединение с сервером.')
                    self.running = False
                    self.connection_lost.emit()
                else:
                    CLIENT_LOGGER.debug(f'Принято сообщение с сервера: {message}')
                    self.process_server_ans(message)
                finally:
                    self.transport.settimeout(5)


if __name__ == '__main__':
    attr = arg_parser('client', DEFAULT_PORT, DEFAULT_IP_ADDRESS)
    server_address = attr.address
    server_port = attr.port
    client_name = attr.name
    client_app = QApplication(sys.argv)
    if not client_name:
        start_dialog = StartDialog()
        client_app.exec_()
        if start_dialog.start_pressed:
            client_name = start_dialog.start_ui.lineEditUserName.text()
            del start_dialog
        else:
            sys.exit(0)
    CLIENT_LOGGER.info(
        f'Запущен клиент с парамерами: адрес сервера: {server_address} , '
        f'порт: {server_port}, имя пользователя: {client_name}')
    path_db = os.path.abspath(os.path.join(os.path.dirname(__file__), './'))
    database = ClientDB(client_name, path_db)
    try:
        transport = ClientTransport(server_port, server_address, database, client_name)
    except OSError as error:
        print(error)
        sys.exit(1)
    else:
        transport.daemon = True
        transport.start()
    main_window = ClientMainWindow(transport, database)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Чат Программа alpha release - {client_name}')
    client_app.exec_()
    transport.transport_shutdown()
    transport.join()
