import binascii
import hashlib
import hmac
import os
import socket
import sys
import time
import threading
from json import JSONDecodeError
from Crypto.PublicKey import RSA
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication, QMessageBox

sys.path.append('../')
from client_db import ClientDB
from client_gui import StartDialog, ClientMainWindow
from common.decorators import loger
from common.errors import ServerError
from common.settings import PRESENCE, RESPONSE, ERROR, ACTION, MESSAGE, \
    EXIT, ADD_CONTACT, REMOVE_CONTACT, GET_CONTACTS, USERS_REQUEST, MESSAGE_TEXT, \
    LIST_INFO, SENDER, DESTINATION, TIME, ACCOUNT_NAME, USER, DEFAULT_PORT, \
    DEFAULT_IP_ADDRESS, PUBLIC_KEY, DATA, RESPONSE_511, PUBLIC_KEY_REQUEST
from common.utilites import getting, sending, arg_parser
from log import client_log_config

CLIENT_LOGGER = client_log_config.LOGGER
socket_lock = threading.Lock()


@loger
class ClientTransport(threading.Thread, QObject):
    """
    Класс реализующий транспортную подсистему клиентского
    модуля. Отвечает за взаимодействие с сервером.
    """
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()
    message_205 = pyqtSignal()

    def __init__(self, port, ip_address, database, username, passwd, keys):
        """
        Конструктор класса клиентского модуля.
        :param port: int - порт для соединения с сервером.
        :param ip_address: str - адрес сервера.
        :param database: object - объект базы данных.
        :param username: str - имя пользователя.
        :param passwd: str - пароль пользователя.
        :param keys: str - ключи пользователя.
        """
        threading.Thread.__init__(self)
        QObject.__init__(self)
        self.database = database
        self.username = username
        self.password = passwd
        self.keys = keys
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
        """
        Метод отвечающий за устанновку соединения с сервером.
        :param port: int - порт для соединения с сервером.
        :param ip: str - адрес сервера.
        :return: None.
        """
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
                CLIENT_LOGGER.debug("Соединение установлено.")
                break
            time.sleep(1)
        if not connected:
            CLIENT_LOGGER.critical('Не удалось установить соединение с сервером')
            raise ServerError('Не удалось установить соединение с сервером')
        CLIENT_LOGGER.debug('Запуск диалога авторизации.')
        passwd_bytes = self.password.encode('utf-8')
        salt = self.username.lower().encode('utf-8')
        passwd_hash = hashlib.pbkdf2_hmac('sha512', passwd_bytes, salt, 10000)
        passwd_hash_string = binascii.hexlify(passwd_hash)
        CLIENT_LOGGER.debug(f'Хеш пароля готов: {passwd_hash_string}')
        pubkey = self.keys.publickey().export_key().decode('ascii')
        with socket_lock:
            presence = {
                ACTION: PRESENCE,
                TIME: time.time(),
                USER: {
                    ACCOUNT_NAME: self.username,
                    PUBLIC_KEY: pubkey
                }
            }
            CLIENT_LOGGER.debug(f"Presence сообщение = {presence}")
            try:
                sending(self.transport, presence)
                ans = getting(self.transport)
                CLIENT_LOGGER.debug(f'Ответ сервера = {ans}.')
                if RESPONSE in ans:
                    if ans[RESPONSE] == 400:
                        raise ServerError(ans[ERROR])
                    elif ans[RESPONSE] == 511:
                        ans_data = ans[DATA]
                        _hash = hmac.new(passwd_hash_string, ans_data.encode('utf-8'), 'MD5')
                        digest = _hash.digest()
                        my_ans = RESPONSE_511
                        my_ans[DATA] = binascii.b2a_base64(digest).decode('ascii')
                        sending(self.transport, my_ans)
                        self.process_server_ans(getting(self.transport))
            except (OSError, JSONDecodeError) as err:
                CLIENT_LOGGER.debug('Ошибка соединения.', exc_info=err)
                raise ServerError('Сбой соединения в процессе авторизации.')

    def process_server_ans(self, message):
        """
        Метод обработчик поступающих сообщений с сервера.
        :param message: dict - принятое сообщение.
        :return: None.
        """
        CLIENT_LOGGER.debug(f'Разбор сообщения от сервера: {message}')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return
            elif message[RESPONSE] == 400:
                raise ServerError(f'{message[ERROR]}')
            elif message[RESPONSE] == 205:
                self.user_list_update()
                self.contacts_list_update()
                self.message_205.emit()
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
            self.new_message.emit(message[SENDER])

    def contacts_list_update(self):
        """
        Метод обновляющий с сервера список контактов.
        :return: None
        """
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
        """
        Метод обновляющий с сервера список пользователей.
        :return: None
        """
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

    def key_request(self, user):
        """
        Метод запрашивающий с сервера публичный ключ пользователя.
        :param user: str - имя пользователя.
        :return: None.
        """
        CLIENT_LOGGER.debug(f'Запрос публичного ключа для {user}')
        req = {
            ACTION: PUBLIC_KEY_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: user
        }
        with socket_lock:
            sending(self.transport, req)
            ans = getting(self.transport)
        if RESPONSE in ans and ans[RESPONSE] == 511:
            return ans[DATA]
        else:
            CLIENT_LOGGER.error(f'Не удалось получить ключ собеседника{user}.')

    def add_contact(self, contact):
        """
        Метод отправляющий на сервер сведения о добавлении контакта.
        :param contact: str - имя контакта.
        :return: None.
        """
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
        """
        Метод отправляющий на сервер сведения об удалении контакта.
        :param contact: str - имя контакта.
        :return: None.
        """
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
        """Метод уведомляющий сервер о завершении работы клиента.
        :return: None.
        """
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
        """
        Метод отправляющий на сервер сообщения для пользователя.
        :param to: str - имя пользователя которому отправляется сообщение.
        :param message: dict - словарь сообщения.
        :return: None.
        """
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
        """
        Метод содержащий основной цикл работы транспортного потока.
        :return: None.
        """
        CLIENT_LOGGER.debug('Запущен процесс - приёмник сообщений с сервера.')
        while self.running:
            time.sleep(1)
            message = None
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
                finally:
                    self.transport.settimeout(5)
            if message:
                CLIENT_LOGGER.debug(f'Принято сообщение с сервера: {message}')
                self.process_server_ans(message)


if __name__ == '__main__':
    attr = arg_parser('client', DEFAULT_PORT, DEFAULT_IP_ADDRESS)
    server_address = attr.address
    server_port = attr.port
    client_name = attr.name
    client_passwd = attr.password
    client_app = QApplication(sys.argv)
    start_dialog = StartDialog()
    if not client_name or not client_passwd:
        client_app.exec_()
        if start_dialog.start_pressed:
            client_name = start_dialog.start_ui.lineEditUserName.text()
            client_passwd = start_dialog.start_ui.lineEditPassword.text()
            CLIENT_LOGGER.debug(
                f'Использовано USERNAME = {client_name}, PASSWD = {client_passwd}.'
            )
        else:
            sys.exit(0)
    CLIENT_LOGGER.info(
        f'Запущен клиент с парамерами: адрес сервера: {server_address} , '
        f'порт: {server_port}, имя пользователя: {client_name}')
    path_db = os.path.abspath(os.path.join(os.path.dirname(__file__), './'))
    dir_path = os.path.dirname(os.path.realpath(__file__))
    key_file = os.path.join(dir_path, f'{client_name}.key')
    if not os.path.exists(key_file):
        keys = RSA.generate(2048, os.urandom)
        with open(key_file, 'wb') as key:
            key.write(keys.export_key())
    else:
        with open(key_file, 'rb') as key:
            keys = RSA.import_key(key.read())
    CLIENT_LOGGER.debug("Ключи успешно загружены.")
    database = ClientDB(client_name, path_db)
    try:
        transport = ClientTransport(
            server_port, server_address,
            database, client_name,
            client_passwd, keys
        )
        CLIENT_LOGGER.debug("Транспорт готов.")
    except ServerError as error:
        message = QMessageBox()
        message.critical(start_dialog, 'Ошибка сервера', error.text)
        sys.exit(1)
    transport.daemon = True
    transport.start()
    del start_dialog
    main_window = ClientMainWindow(transport, database, keys)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Чат Программа alpha release - {client_name}')
    client_app.exec_()
    transport.transport_shutdown()
    transport.join()
