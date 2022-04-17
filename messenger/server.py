import select
import socket

from common.decorators import loger
from common.settings import ACTION, RESPONSE, MAX_CONNECTIONS, PRESENCE, TIME, ACCOUNT_NAME, \
    ERROR, MESSAGE, SENDER, MESSAGE_TEXT, DESTINATION, EXIT
from common.utilites import getting, sending, arg_parser
from log import server_log_config
from descriptors import Port
from metaclasses import ServerMaker

SERVER_LOGGER = server_log_config.LOGGER


@loger
class Server(metaclass=ServerMaker):
    port = Port()

    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.clients = []
        self.messages = []
        self.names = {}

    def process(self, message, client=None, listen_socks=None):
        SERVER_LOGGER.debug(f'Разбор сообщения {message} от клиента')
        if ACTION in message and message[ACTION] == PRESENCE and TIME in message \
                and ACCOUNT_NAME in message:
            if message[ACCOUNT_NAME] not in self.names.keys():
                self.names[message[ACCOUNT_NAME]] = client
                sending(client, {RESPONSE: 200})
                return
            else:
                sending(client, {RESPONSE: 400, ERROR: 'Имя пользователя уже занято.'})
                self.clients.remove(client)
                client.close()
            return
        elif ACTION in message and message[ACTION] == MESSAGE and DESTINATION in message \
                and TIME in message and SENDER in message and MESSAGE_TEXT in message:
            self.messages.append(message)
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
                return
            return
        elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
            self.clients.remove(self.names[ACCOUNT_NAME])
            self.names[ACCOUNT_NAME].close()
            del self.names[ACCOUNT_NAME]
            return
        else:
            sending(client, {RESPONSE: 400, ERROR: 'Bad Request'})
            return

    def start(self):
        SERVER_LOGGER.info(f'Запущен сервер. '
                           f'Адрес(а) с которого(ых) принимаются подключения:'
                           f' {"любой" if not self.address else self.address}, '
                           f'Порт для подключений: {self.port}')
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.bind((self.address, self.port))
        transport.settimeout(0.5)
        SERVER_LOGGER.info(f'Сервер начал прослушивание{" всех" if not self.address else ""}'
                           f' адреса(ов) {"," if not self.address else ": " + self.address + ","}'
                           f' Порт для подключений: {self.port}')
        transport.listen(MAX_CONNECTIONS)
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
                    recv_data_lst, send_data_lst, err_lst = select.select(self.clients, self.clients, [], 0)
            except OSError:
                pass
            if recv_data_lst:
                for client_with_message in recv_data_lst:
                    try:
                        self.process(getting(client_with_message), client=client_with_message)
                    except Exception as err:
                        SERVER_LOGGER.info(f'Клиент {client_with_message.getpeername()}'
                                           f' отключился от сервера. {err}')
                        self.clients.remove(client_with_message)
            for message in self.messages:
                try:
                    self.process(message, listen_socks=send_data_lst)
                except Exception as err:
                    SERVER_LOGGER.info(f'Связь с клиентом с именем {message[DESTINATION]} была потеряна. {err}')
                    self.clients.remove(self.names[message[DESTINATION]])
                    del self.names[message[DESTINATION]]
                self.messages.clear()
            if err_lst:
                for client_with_error in err_lst:
                    SERVER_LOGGER.info(f'Клиент {client_with_error.getpeername()}'
                                       f' отключился от сервера.')
                    self.clients.remove(client_with_error)


if __name__ == '__main__':
    attr = arg_parser('server')
    listen_address = attr.address
    listen_port = attr.port
    server = Server(listen_address, listen_port)
    server.start()
