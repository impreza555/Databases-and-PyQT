import os
import sys

from Crypto.PublicKey import RSA
from PyQt5.QtWidgets import QApplication, QMessageBox

sys.path.append('../')
from client.client_db import ClientDB
from client.client_gui import StartDialog, ClientMainWindow
from client.client_main import ClientTransport
from client.common.decorators import log
from client.common.errors import ServerError
from client.common.settings import DEFAULT_PORT, DEFAULT_IP_ADDRESS
from client.common.utilites import arg_parser
from client.log import client_log_config

CLIENT_LOGGER = client_log_config.LOGGER


@log
def main():
    """
    Функция запускающая основной цикл программы клиента.
    :return: None.
    """
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


if __name__ == '__main__':
    main()
