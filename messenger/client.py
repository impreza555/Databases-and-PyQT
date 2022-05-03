import os
import socket
import threading
import time
from json import JSONDecodeError
from sys import exit

from common.decorators import loger
from common.settings import PRESENCE, RESPONSE, ERROR, ACTION, MESSAGE, \
    EXIT, ADD_CONTACT, REMOVE_CONTACT, GET_CONTACTS, USERS_REQUEST, MESSAGE_TEXT, \
    LIST_INFO, SENDER, DESTINATION, TIME, ACCOUNT_NAME, USER, DEFAULT_PORT, DEFAULT_IP_ADDRESS
from common.utilites import getting, sending, arg_parser
from log import client_log_config
from metaclasses import ClientMaker
from db_creators.client_db import ClientDB

CLIENT_LOGGER = client_log_config.LOGGER


@loger
class Client(metaclass=ClientMaker):
    def __init__(self, address, port, account_name):
        self.path = os.path.abspath(os.path.join(os.path.dirname(__file__), './'))
        self.address = address
        self.port = port
        self.name = account_name
        if not self.name:
            self.name = input('Введите имя пользователя: ')
        self.database = ClientDB(self.name, self.path)
        self.help = 'Доступные команды:\n' \
                    'help - получение справки по командам.\n' \
                    'message - отправить сообщение.\n' \
                    'contacts - получить список контактов.\n' \
                    'edit - редактирование контактов.\n' \
                    'history - получить историю сообщений.\n' \
                    'exit - выход из программы.\n'
        self.sock_lock = threading.Lock()
        self.database_lock = threading.Lock()

    def database_load(self, sock, database, username):
        try:
            users_list = self.user_list_request(sock, username)
        except Exception as e:
            CLIENT_LOGGER.error(f'Ошибка запроса списка известных пользователей. {e}')
        else:
            database.add_users(users_list)
        try:
            contacts_list = self.contacts_list_request(sock, username)
        except Exception as e:
            CLIENT_LOGGER.error(f'Ошибка запроса списка контактов. {e}')
        else:
            for contact in contacts_list:
                database.add_contact(contact)

    def user_list_request(self, sock, username):
        CLIENT_LOGGER.debug(f'Запрос списка известных пользователей {username}')
        req = {
            ACTION: USERS_REQUEST,
            TIME: time.time(),
            ACCOUNT_NAME: username
        }
        sending(sock, req)
        ans = getting(sock)
        if RESPONSE in ans and ans[RESPONSE] == 202:
            return ans[LIST_INFO]
        else:
            raise OSError('Не удалось получить список известных пользователей.')

    def contacts_list_request(self, sock, user_name):
        CLIENT_LOGGER.debug(f'Запрос контакт листа для пользователя {user_name}')
        req = {
            ACTION: GET_CONTACTS,
            TIME: time.time(),
            ACCOUNT_NAME: user_name
        }
        CLIENT_LOGGER.debug(f'Сформирован запрос {req}')
        sending(sock, req)
        ans = getting(sock)
        CLIENT_LOGGER.debug(f'Получен ответ {ans}')
        if RESPONSE in ans and ans[RESPONSE] == 202:
            return ans[LIST_INFO]
        else:
            raise OSError('Не удалось получить список контактов.')

    def response(self, message):
        CLIENT_LOGGER.debug(f'Разбор сообщения {message} от сервера')
        if RESPONSE in message:
            if message[RESPONSE] == 200:
                return 'Соединение установлено'
            return f'Ошибка соединения с сервером: {message[ERROR]}'
        CLIENT_LOGGER.error('Неверный формат сообщения от сервера')
        raise ValueError

    def process(self, transport, username):
        while True:
            time.sleep(1)
            with self.sock_lock:
                try:
                    message = getting(transport)
                except OSError as err:
                    if err.errno:
                        CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
                        break
                except (ConnectionError, ConnectionAbortedError,
                        ConnectionResetError, JSONDecodeError):
                    CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
                    break
                except Exception as e:
                    CLIENT_LOGGER.error(f'Неизвестная ошибка при получении сообщения. {e}')
                    break
                else:
                    CLIENT_LOGGER.debug(f'Разбор сообщения {message} от сервера')
                    if ACTION in message and message[ACTION] == MESSAGE and SENDER in message \
                            and DESTINATION in message and MESSAGE_TEXT in message \
                            and message[DESTINATION] == username:
                        print(f'Получено сообщение от пользователя '
                              f'{message[SENDER]}:\n{"-" * 50}\n{message[MESSAGE_TEXT]}')
                        CLIENT_LOGGER.info(f'Получено сообщение от пользователя'
                                           f' {message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                        with self.database_lock:
                            try:
                                self.database.save_message(message[SENDER], username,
                                                           message[MESSAGE_TEXT])
                            except Exception as e:
                                print(e)
                                CLIENT_LOGGER.error(f'Ошибка взаимодействия с базой данных. {e}')

                        CLIENT_LOGGER.info(f'Получено сообщение от пользователя '
                                           f'{message[SENDER]}:\n{message[MESSAGE_TEXT]}')
                    else:
                        CLIENT_LOGGER.error(f'Получено некорректное сообщение с сервера: {message}')

    def creating_message(self, action, sock, user_name):
        message = None
        if action == PRESENCE:
            message = {
                ACTION: action,
                TIME: time.time(),
                ACCOUNT_NAME: user_name
            }
            CLIENT_LOGGER.debug(f'Сформировано {PRESENCE} сообщение от пользователя {user_name}')
        elif action == MESSAGE:
            to_user = input('Введите получателя сообщения: ')
            message_text = input('Введите сообщение для отправки или отправьте пустое сообщение'
                                 ' для завершения работы: ')
            if not message_text:
                sock.close()
                CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
                exit(0)
            with self.database_lock:
                if not self.database.check_user(to_user):
                    CLIENT_LOGGER.error(f'Попытка отправить сообщение'
                                        f' незарегистрированному получателю: {to_user}')
                    return
            message = {
                ACTION: action,
                SENDER: user_name,
                DESTINATION: to_user,
                TIME: time.time(),
                MESSAGE_TEXT: message_text
            }
            CLIENT_LOGGER.debug(f'Сформировано сообщение : {message} для пользователя {to_user}')
            with self.database_lock:
                self.database.save_message(user_name, to_user, message_text)
            # self.database.save_message(user_name, to_user, message)
        elif action == EXIT:
            message = {
                ACTION: action,
                TIME: time.time(),
                ACCOUNT_NAME: user_name
            }
        return message

    def add_contact(self, sock, user_name, contact):
        CLIENT_LOGGER.debug(f'Создание контакта {contact}')
        req = {
            ACTION: ADD_CONTACT,
            TIME: time.time(),
            ACCOUNT_NAME: user_name,
            USER: contact
        }
        sending(sock, req)
        ans = getting(sock)
        if RESPONSE in ans and ans[RESPONSE] == 200:
            pass
        else:
            raise OSError('Ошибка создания контакта')
        print('Удачное создание контакта.')

    def remove_contact(self, sock, username, contact):
        CLIENT_LOGGER.debug(f'Создание контакта {contact}')
        req = {
            ACTION: REMOVE_CONTACT,
            TIME: time.time(),
            ACCOUNT_NAME: username,
            USER: contact
        }
        sending(sock, req)
        ans = getting(sock)
        if RESPONSE in ans and ans[RESPONSE] == 200:
            pass
        else:
            raise OSError('Ошибка удаления клиента')
        print('Удачное удаление')

    def edit_contacts(self, sock, user_name):
        ans = input('Для удаления введите del, для добавления add: ')
        if ans == 'del':
            contact = input('Введите имя удаляемого контакта: ')
            with self.database_lock:
                if self.database.check_contact(contact):
                    self.database.del_contact(contact)
                else:
                    CLIENT_LOGGER.error('Попытка удаления несуществующего контакта.')
            with self.sock_lock:
                try:
                    self.remove_contact(sock, user_name, contact)
                except Exception as e:
                    CLIENT_LOGGER.error(f'Не удалось отправить информацию на сервер. {e}')
        elif ans == 'add':
            contact = input('Введите имя добавляемого контакта: ')
            if self.database.check_user(contact):
                with self.database_lock:
                    self.database.add_contact(contact)
                with self.sock_lock:
                    try:
                        self.add_contact(sock, user_name, contact)
                    except Exception as e:
                        CLIENT_LOGGER.error(f'Не удалось отправить информацию на сервер. {e}')

    def print_history(self, user_name):
        ask = input('Показать входящие сообщения - in, исходящие - out, все - просто Enter: ')
        with self.database_lock:
            if ask == 'in':
                history_list = self.database.get_history(to_who=user_name)
                for message in history_list:
                    print(f'\nСообщение от пользователя: {message[0]} '
                          f'от {message[3]}:\n{message[2]}')
            elif ask == 'out':
                history_list = self.database.get_history(from_who=user_name)
                for message in history_list:
                    print(f'\nСообщение пользователю: {message[1]} '
                          f'от {message[3]}:\n{message[2]}')
            else:
                history_list = self.database.get_history()
                for message in history_list:
                    print(f'\nСообщение от пользователя: {message[0]},'
                          f' пользователю {message[1]} '
                          f'от {message[3]}\n{message[2]}')

    def dialogue_with_user(self, sock, user_name):
        print('Добро пожаловать в программу для общения по сети.')
        while True:
            command = input(f'{user_name}, введите команду.'
                            f' Help - вывести список команд:\n ').lower()
            if command == 'help':
                print(self.help)
            elif command == 'message':
                message = self.creating_message(MESSAGE, sock, user_name)
                with self.sock_lock:
                    try:
                        sending(sock, message)
                        CLIENT_LOGGER.info(f'Отправлено сообщение для пользователя'
                                           f' {message[DESTINATION]}')
                    except OSError as err:
                        if err.errno:
                            CLIENT_LOGGER.critical('Потеряно соединение с сервером.')
                            exit(1)
                        else:
                            CLIENT_LOGGER.error('Не удалось передать сообщение. Таймаут соединения')
            elif command == 'exit':
                message = self.creating_message(EXIT, sock, user_name)
                with self.sock_lock:
                    try:
                        sending(sock, message)
                    except Exception as e:
                        CLIENT_LOGGER.error(f'Ошибка отправки сообщения на сервер: {e}')
                        pass
                print('Завершение соединения.')
                CLIENT_LOGGER.info('Завершение работы по команде пользователя.')
                time.sleep(0.5)
                break
            elif command == 'contacts':
                with self.database_lock:
                    contacts_list = self.database.get_contacts()
                for contact in contacts_list:
                    print(contact)
            elif command == 'edit':
                self.edit_contacts(sock, user_name)
            elif command == 'history':
                self.print_history(user_name)
            else:
                print('Команда не распознана, попробуйте снова.')
                print(self.help)

    def start(self):
        try:
            transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            transport.settimeout(1)
            transport.connect((self.address, self.port))
            CLIENT_LOGGER.info(f'Подключение к серверу {self.address}:{self.port}')
            presence_message = self.creating_message(PRESENCE, transport, self.name)
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
        except Exception as e:
            CLIENT_LOGGER.critical(f'Неизвестная ошибка: {e}')
            exit(1)
        else:
            self.database_load(transport, self.database, self.name)
            sender = threading.Thread(target=self.dialogue_with_user, args=(transport, self.name))
            sender.daemon = True
            sender.start()
            receiver = threading.Thread(target=self.process, args=(transport, self.name))
            receiver.daemon = True
            receiver.start()
            CLIENT_LOGGER.debug('Запущены процессы')
            while True:
                time.sleep(1)
                if receiver.is_alive() and sender.is_alive():
                    continue
                break


if __name__ == '__main__':
    attr = arg_parser('client', DEFAULT_PORT, DEFAULT_IP_ADDRESS)
    connect_address = attr.address
    connect_port = attr.port
    name = attr.name
    client = Client(connect_address, connect_port, name)
    client.start()
