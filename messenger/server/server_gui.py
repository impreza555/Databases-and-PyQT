import binascii
import hashlib
import os

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QApplication, qApp, QDialog, \
    QFileDialog, QMessageBox, QLineEdit
from server.server_ui import Ui_ServerGui
from server.set_server_ui import Ui_DialogSetServer
from server.register_user_ui import Ui_RegUser
from server.del_user_dialog_ui import Ui_DelUser


class MainWindow(QMainWindow):
    """
    Класс главного окна сервера
    """

    def __init__(self, database, server, config):
        """
        Конструктор класса главного окна сервера
        :param database: object - объект базы данных
        :param server: object - объект сервера
        :param config: object - объект конфигурации
        """
        super().__init__()
        self.database = database
        self.server_thread = server
        self.config = config
        self.main_ui = Ui_ServerGui()
        self.main_ui.setupUi(self)
        self.main_ui.exitAction.setShortcut('Ctrl+Q')
        self.main_ui.exitAction.triggered.connect(qApp.quit)
        self.main_ui.statusbarServer.showMessage('Сервер запущен')
        self.timer = QTimer()
        self.timer.timeout.connect(self.gui_create_model)
        self.timer.timeout.connect(self.create_stat_model)
        self.timer.start(1000)
        self.main_ui.refreshAction.triggered.connect(self.gui_create_model)
        self.main_ui.configAction.triggered.connect(self.server_config)
        self.main_ui.actionRegisterUser.triggered.connect(self.reg_user)
        self.main_ui.actionDelUser.triggered.connect(self.del_user)

    def gui_create_model(self):
        """
        Метод заполняющий таблицу активных пользователей.
        :return: None
        """
        list_users = self.database.active_users_list()
        list_table = QStandardItemModel()
        list_table.setHorizontalHeaderLabels(
            ['Имя Клиента', 'IP Адрес', 'Порт', 'Время подключения']
        )
        for row in list_users:
            user, ip, port, time = row
            user = QStandardItem(user)
            user.setEditable(False)
            ip = QStandardItem(ip)
            ip.setEditable(False)
            port = QStandardItem(str(port))
            port.setEditable(False)
            time = QStandardItem(str(time.replace(microsecond=0)))
            time.setEditable(False)
            list_table.appendRow([user, ip, port, time])
        self.main_ui.tableViewListClients.setModel(list_table)
        self.main_ui.tableViewListClients.resizeColumnsToContents()
        self.main_ui.tableViewListClients.resizeRowsToContents()

    def create_stat_model(self):
        """
        Метод реализующий заполнение таблицы статистикой сообщений.
        :return: None
        """
        hist_list = self.database.message_history()
        list_table = QStandardItemModel()
        list_table.setHorizontalHeaderLabels(
            ['Имя Клиента', 'Последний раз входил', 'Сообщений отправлено', 'Сообщений получено']
        )
        for row in hist_list:
            user, last_seen, sent, recvd = row
            user = QStandardItem(user)
            user.setEditable(False)
            last_seen = QStandardItem(str(last_seen.replace(microsecond=0)))
            last_seen.setEditable(False)
            sent = QStandardItem(str(sent))
            sent.setEditable(False)
            recvd = QStandardItem(str(recvd))
            recvd.setEditable(False)
            list_table.appendRow([user, last_seen, sent, recvd])
        self.main_ui.tableViewStatClients.setModel(list_table)
        self.main_ui.tableViewStatClients.resizeColumnsToContents()
        self.main_ui.tableViewStatClients.resizeRowsToContents()

    def server_config(self):
        """
        Метод создающий окно с настройками сервера.
        :return: None
        """
        global config_window
        config_window = ConfigWindow(self.config)

    def reg_user(self):
        """
        Метод создающий окно регистрации пользователя.
        :return: None
        """
        global reg_window
        reg_window = RegisterUser(self.database, self.server_thread)
        reg_window.show()

    def del_user(self):
        """
        Метод создающий окно удаления пользователя.
        :return: None
        """
        global del_window
        del_window = DelUserDialog(self.database, self.server_thread)
        del_window.show()


class ConfigWindow(QDialog):
    """
    Класс окна настроек сервера
    """

    def __init__(self, config):
        """
        Конструктор класса окна настроек сервера
        :param config: object - объект конфигурации
        """
        super().__init__()
        self.config = config
        self.config_ui = Ui_DialogSetServer()
        self.config_ui.setupUi(self)
        self.config_ui.pushButtonDbPathSelect.clicked.connect(self.open_file_dialog)
        self.config_ui.pushButtonClose.clicked.connect(self.close)
        self.show()
        self.config_ui.lineEditDbPath.insert(self.config['SETTINGS']['Database_path'])
        self.config_ui.lineEditDbFile.insert(self.config['SETTINGS']['Database_file'])
        self.config_ui.lineEditPort.insert(self.config['SETTINGS']['Default_port'])
        self.config_ui.lineEditIP.insert(self.config['SETTINGS']['Listen_Address'])
        self.config_ui.pushButtonSave.clicked.connect(self.save_server_config)

    def open_file_dialog(self):
        """
        Метод обработчик открытия окна выбора папки.
        :return: None
        """
        global dialog
        dialog = QFileDialog(self)
        path = dialog.getExistingDirectory()
        path = path.replace('/', '\\')
        self.config_ui.lineEditDbPath.clear()
        self.config_ui.lineEditDbPath.insert(path)

    def save_server_config(self):
        """
        Метод сохранения настроек.
        Проверяет правильность введённых данных и
        если всё правильно сохраняет ini файл.
        :return: None
        """
        global config_window
        message = QMessageBox()
        self.config['SETTINGS']['Database_path'] = self.config_ui.lineEditDbPath.text()
        self.config['SETTINGS']['Database_file'] = self.config_ui.lineEditDbFile.text()
        try:
            port = int(self.config_ui.lineEditPort.text())
        except ValueError:
            message.warning(self, 'Ошибка', 'Порт должен быть числом')
        else:
            self.config['SETTINGS']['Listen_Address'] = self.config_ui.lineEditIP.text()
            if 1023 < port < 65536:
                self.config['SETTINGS']['Default_port'] = str(port)
                dir_path = os.path.dirname(os.path.realpath(__file__))
                dir_path = os.path.join(dir_path, '..')
                with open(f"{dir_path}/{'server.ini'}", 'w') as conf:
                    self.config.write(conf)
                    message.information(self, 'OK', 'Настройки успешно сохранены!')
            else:
                message.warning(self, 'Ошибка', 'Порт должен быть от 1024 до 65536')


class RegisterUser(QDialog):
    """
    Класс окна регистрации пользователя
    """

    def __init__(self, database, server):
        """
        Конструктор класса окна регистрации пользователя
        :param database: object - объект базы данных
        :param server: object - объект сервера
        """
        super().__init__()
        self.database = database
        self.server = server
        self.reg_ui = Ui_RegUser()
        self.reg_ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)
        self.reg_ui.lineEditPassword.setEchoMode(QLineEdit.Password)
        self.reg_ui.lineEditPassword_2.setEchoMode(QLineEdit.Password)
        self.reg_ui.pushButtonSave.clicked.connect(self.save_data)
        self.reg_ui.pushButtonCancel.clicked.connect(self.close)
        self.messages = QMessageBox()
        self.show()

    def save_data(self):
        """
        Метод проверки правильности ввода и сохранения в базу нового пользователя.
        :return: None
        """
        if not self.reg_ui.lineEditUserName.text():
            self.messages.critical(
                self, 'Ошибка', 'Не указано имя пользователя.'
            )
            return
        elif self.reg_ui.lineEditPassword.text() != self.reg_ui.lineEditPassword_2.text():
            self.messages.critical(
                self, 'Ошибка', 'Введённые пароли не совпадают.'
            )
            return
        elif self.database.check_user(self.reg_ui.lineEditUserName.text()):
            self.messages.critical(
                self, 'Ошибка', 'Пользователь уже существует.'
            )
            return
        else:
            passwd_bytes = self.reg_ui.lineEditPassword.text().encode('utf-8')
            salt = self.reg_ui.lineEditUserName.text().lower().encode('utf-8')
            passwd_hash = hashlib.pbkdf2_hmac(
                'sha512', passwd_bytes, salt, 10000
            )
            self.database.add_user(
                self.reg_ui.lineEditUserName.text(), binascii.hexlify(passwd_hash)
            )
            self.messages.information(
                self, 'Успех', 'Пользователь успешно зарегистрирован.'
            )
            self.server.service_update_lists()
            self.close()


class DelUserDialog(QDialog):
    """
    Класс окна удаления пользователя
    """

    def __init__(self, database, server):
        """
        Конструктор класса окна удаления пользователя
        :param database: object - объект базы данных
        :param server: object - объект сервера
        """
        super().__init__()
        self.database = database
        self.server = server
        self.del_ui = Ui_DelUser()
        self.del_ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)
        self.del_ui.pushButtonDelUser.clicked.connect(self.remove_user)
        self.del_ui.pushButtonCancel.clicked.connect(self.close)
        self.all_users_fill()

    def all_users_fill(self):
        """
        Метод заполняющий список пользователей.
        :return: None
        """
        self.del_ui.comboBoxSelectUser.addItems(
            [item[0] for item in self.database.users_list()]
        )

    def remove_user(self):
        """
        Метод - обработчик удаления пользователя.
        :return: None
        """
        self.database.remove_user(self.del_ui.comboBoxSelectUser.currentText())
        if self.del_ui.comboBoxSelectUser.currentText() in self.server.names:
            sock = self.server.names[self.del_ui.comboBoxSelectUser.currentText()]
            del self.server.names[self.del_ui.comboBoxSelectUser.currentText()]
            self.server.remove_client(sock)
        self.server.service_update_lists()
        self.close()


if __name__ == '__main__':
    pass
    # app = QApplication([])
    # from server_db import ServerDB
    # database = ServerDB('../server_database.db3')
    # import os
    # import sys
    # path1 = os.path.join(os.getcwd(), '..')
    # sys.path.insert(0, path1)
    # from server_main import Server
    # server = Server('127.0.0.1', 7777, database)
    # dial = RegisterUser(database, server)
    # app.exec_()

    # app = QApplication([])
    # from server_db import ServerDB
    # database = ServerDB('../server_database.db3')
    # import os
    # import sys
    # path1 = os.path.join(os.getcwd(), '..')
    # sys.path.insert(0, path1)
    # from server_main import Server
    # server = Server('127.0.0.1', 7777, database)
    # dial = DelUserDialog(database, server)
    # dial.show()
    # app.exec_()
