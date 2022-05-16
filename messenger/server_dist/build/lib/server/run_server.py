import configparser
import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

sys.path.append('../../client_dist/')
from common.decorators import log
from common.settings import DEFAULT_PORT
from common.utilites import arg_parser
from server.server_db import ServerDB
from server.server_gui import MainWindow
from server.server_main import Server


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
    Функция запускающая основной цикл программы сервера.
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
