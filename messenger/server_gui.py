import sys

from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QApplication, qApp, QDialog, QFileDialog
from server_ui import Ui_ServerGui
from set_server_ui import Ui_DialogSetServer


def gui_create_model(database):
    list_users = database.active_users_list()
    list_table = QStandardItemModel()
    list_table.setHorizontalHeaderLabels(['Имя Клиента', 'IP Адрес', 'Порт', 'Время подключения'])
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
    return list_table


def create_stat_model(database):
    hist_list = database.message_history()
    list_table = QStandardItemModel()
    list_table.setHorizontalHeaderLabels(
        ['Имя Клиента', 'Последний раз входил', 'Сообщений отправлено', 'Сообщений получено'])
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
    return list_table


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_ui = Ui_ServerGui()
        self.main_ui.setupUi(self)
        self.main_ui.exitAction.setShortcut('Ctrl+Q')
        self.main_ui.exitAction.triggered.connect(qApp.quit)
        self.show()


class ConfigWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.config_ui = Ui_DialogSetServer()
        self.config_ui.setupUi(self)

        def open_file_dialog():
            global dialog
            dialog = QFileDialog(self)
            path = dialog.getExistingDirectory()
            path = path.replace('/', '\\')
            self.config_ui.lineEditDbPath.insert(path)

        self.config_ui.pushButtonDbPathSelect.clicked.connect(open_file_dialog)
        self.config_ui.pushButtonClose.clicked.connect(self.close)
        self.show()


if __name__ == '__main__':
    # app = QApplication(sys.argv)
    # application = MainWindow()
    # application.main_ui.statusbarServer.showMessage('Тестовое сообщение в статус баре')
    # test_list = QStandardItemModel(application)
    # test_list.setHorizontalHeaderLabels(['Имя Клиента', 'IP Адрес',
    #                                      'Порт', 'Время подключения'])
    # test_list.appendRow(
    #     [QStandardItem('test1'), QStandardItem('192.198.0.5'),
    #      QStandardItem('23544'), QStandardItem('16:20:34')]
    # )
    # test_list.appendRow(
    #     [QStandardItem('test2'), QStandardItem('192.198.0.8'),
    #      QStandardItem('33245'), QStandardItem('16:22:11')]
    # )
    # application.main_ui.tableViewListClients.setModel(test_list)
    # application.main_ui.tableViewListClients.resizeColumnsToContents()
    #
    # test_list_2 = QStandardItemModel(application)
    # test_list_2.setHorizontalHeaderLabels(['Имя Клиента', 'Последний раз входил',
    #                                        'Отправлено', 'Получено'])
    # test_list_2.appendRow(
    #     [QStandardItem('test1'), QStandardItem('Fri Dec 12 16:20:34 2020'),
    #      QStandardItem('2'), QStandardItem('3')]
    # )
    # test_list_2.appendRow(
    #     [QStandardItem('test2'), QStandardItem('Fri Dec 12 16:23:12 2020'),
    #      QStandardItem('8'), QStandardItem('5')]
    # )
    # application.main_ui.tableViewStatClients.setModel(test_list_2)
    # application.main_ui.tableViewStatClients.resizeColumnsToContents()
    # sys.exit(app.exec())

    # ----------------------------------------------------------
    app = QApplication(sys.argv)
    dial = ConfigWindow()
    sys.exit(app.exec())
