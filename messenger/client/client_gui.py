import sys

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QBrush, QColor
from PyQt5.QtWidgets import QDialog, qApp, QMainWindow, QMessageBox, QApplication
from Crypto.Cipher import PKCS1_OAEP

sys.path.append('../')
from log import client_log_config
from common.errors import ServerError
from client_main_ui import Ui_ClientMainWindow
from client.start_dialog_ui import Ui_StartDialog
from add_contact_dialog_ui import Ui_AddContact
from del_contact_dialog_ui import Ui_DelContact

CLIENT_LOGGER = client_log_config.LOGGER


class StartDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.start_ui = Ui_StartDialog()
        self.start_ui.setupUi(self)
        self.start_pressed = False
        self.start_ui.pushButtonStart.clicked.connect(self.click)
        self.start_ui.pushButtonCancel.clicked.connect(qApp.exit)
        self.show()

    def click(self):
        if self.start_ui.lineEditUserName.text():
            self.start_pressed = True
            qApp.exit()


class AddContact(QDialog):
    def __init__(self, transport, database):
        super().__init__()
        self.transport = transport
        self.database = database
        self.add_ui = Ui_AddContact()
        self.add_ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)
        self.add_ui.pushButtonCancel.clicked.connect(self.close)
        self.possible_contacts_update()
        self.add_ui.pushButtonRefresh.clicked.connect(self.update_possible_contacts)

    def possible_contacts_update(self):
        self.add_ui.comboBoxSelectUser.clear()
        contacts_list = set(self.database.get_contacts())
        users_list = set(self.database.get_users())
        users_list.remove(self.transport.username)
        self.add_ui.comboBoxSelectUser.addItems(users_list - contacts_list)

    def update_possible_contacts(self):
        try:
            self.transport.user_list_update()
        except OSError:
            pass
        else:
            CLIENT_LOGGER.debug('Обновление списка пользователей с сервера выполнено')
            self.possible_contacts_update()


class DelContact(QDialog):
    """
    Диалог для удаления контакта
    """
    def __init__(self, database):
        super().__init__()
        self.database = database
        self.del_ui = Ui_DelContact()
        self.del_ui.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)
        self.del_ui.comboBoxSelectUser.addItems(sorted(self.database.get_contacts()))
        self.del_ui.pushButtonCancel.clicked.connect(self.close)


class ClientMainWindow(QMainWindow):
    """
    Класс основного окна приложения
    """
    def __init__(self, transport, database, keys):
        """
        Инициализация основного окна
        :param transport: socket - транспорт
        :param database: object - база данных
        :param keys: object - ключи
        """
        super().__init__()
        self.transport = transport
        self.database = database
        self.decrypter = PKCS1_OAEP.new(keys)
        self.main_ui = Ui_ClientMainWindow()
        self.main_ui.setupUi(self)
        self.main_ui.actionExit.triggered.connect(qApp.exit)
        self.main_ui.pushButtonSendMessage.clicked.connect(self.send_message)
        self.main_ui.pushButtonAddContact.clicked.connect(self.add_contact_window)
        self.main_ui.actionAddContact.triggered.connect(self.add_contact_window)
        self.main_ui.pushButtonDelContact.clicked.connect(self.delete_contact_window)
        self.main_ui.actionDelContact.triggered.connect(self.delete_contact_window)
        self.contacts_model = None
        self.history_model = None
        self.messages = QMessageBox()
        self.current_chat = None
        self.main_ui.listViewMessages.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.main_ui.listViewMessages.setWordWrap(True)
        self.main_ui.listViewContacts.doubleClicked.connect(self.select_active_user)
        self.clients_list_update()
        self.set_disabled_input()
        self.show()

    def set_disabled_input(self):
        """
        Метод делающий поля ввода неактивными
        :return: None
        """
        self.main_ui.labelNewMessage.setText('Для выбора получателя'
                                             ' дважды кликните на нем в окне контактов.')
        self.main_ui.textEditMessage.clear()
        if self.history_model:
            self.history_model.clear()
        self.main_ui.pushButtonClearMessage.setDisabled(True)
        self.main_ui.pushButtonSendMessage.setDisabled(True)
        self.main_ui.textEditMessage.setDisabled(True)

    def history_list_update(self):
        """
        Метод заполняющий соответствующий QListView
        историей переписки с текущим собеседником.
        :return: None
        """
        list_messages = sorted(self.database.get_history(self.current_chat),
                               key=lambda item: item[3])
        if not self.history_model:
            self.history_model = QStandardItemModel()
            self.main_ui.listViewMessages.setModel(self.history_model)
        self.history_model.clear()
        length = len(list_messages)
        start_index = 0
        if length > 20:
            start_index = length - 20
        for i in range(start_index, length):
            item = list_messages[i]
            if item[1] == 'in':
                mess = QStandardItem(f'Входящее от {item[3].replace(microsecond=0)}:\n {item[2]}')
                mess.setEditable(False)
                mess.setBackground(QBrush(QColor(255, 213, 213)))
                mess.setTextAlignment(Qt.AlignLeft)
                self.history_model.appendRow(mess)
            else:
                mess = QStandardItem(f'Исходящее от {item[3].replace(microsecond=0)}:\n {item[2]}')
                mess.setEditable(False)
                mess.setTextAlignment(Qt.AlignRight)
                mess.setBackground(QBrush(QColor(204, 255, 204)))
                self.history_model.appendRow(mess)
        self.main_ui.listViewMessages.scrollToBottom()

    def select_active_user(self):
        """
        Метод обработчик события двойного клика по списку контактов.
        :return: None
        """
        self.current_chat = self.main_ui.listViewContacts.currentIndex().data()
        self.set_active_user()

    def set_active_user(self):
        """
        Метод активации чата с собеседником.
        :return: None
        """
        self.main_ui.labelNewMessage.setText(f'Введите сообщение для {self.current_chat}:')
        self.main_ui.pushButtonClearMessage.setDisabled(False)
        self.main_ui.pushButtonSendMessage.setDisabled(False)
        self.main_ui.textEditMessage.setDisabled(False)
        self.history_list_update()

    def clients_list_update(self):
        contacts_list = self.database.get_contacts()
        self.contacts_model = QStandardItemModel()
        for i in sorted(contacts_list):
            item = QStandardItem(i)
            item.setEditable(False)
            self.contacts_model.appendRow(item)
        self.main_ui.listViewContacts.setModel(self.contacts_model)

    def add_contact_window(self):
        global select_dialog
        select_dialog = AddContact(self.transport, self.database)
        select_dialog.add_ui.pushButtonAddUser.clicked.connect(lambda: self.add_contact_action(select_dialog))
        select_dialog.show()

    def add_contact_action(self, item):
        new_contact = item.add_ui.comboBoxSelectUser.currentText()
        self.add_contact(new_contact)
        item.close()

    def add_contact(self, new_contact):
        try:
            self.transport.add_contact(new_contact)
        except ServerError as err:
            self.messages.critical(self, 'Ошибка сервера', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером!')
                self.close()
            self.messages.critical(self, 'Ошибка', 'Таймаут соединения!')
        else:
            self.database.add_contact(new_contact)
            new_contact = QStandardItem(new_contact)
            new_contact.setEditable(False)
            self.contacts_model.appendRow(new_contact)
            CLIENT_LOGGER.info(f'Успешно добавлен контакт {new_contact}')
            self.messages.information(self, 'Успех', 'Контакт успешно добавлен.')

    def delete_contact_window(self):
        global remove_dialog
        remove_dialog = DelContact(self.database)
        remove_dialog.del_ui.pushButtonDelUser.clicked.connect(lambda: self.delete_contact(remove_dialog))
        remove_dialog.show()

    def delete_contact(self, item):
        selected = item.del_ui.comboBoxSelectUser.currentText()
        try:
            self.transport.remove_contact(selected)
        except ServerError as err:
            self.messages.critical(self, 'Ошибка сервера', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером!')
                self.close()
            self.messages.critical(self, 'Ошибка', 'Таймаут соединения!')
        else:
            self.database.del_contact(selected)
            self.clients_list_update()
            CLIENT_LOGGER.info(f'Успешно удалён контакт {selected}')
            self.messages.information(self, 'Успех', 'Контакт успешно удалён.')
            item.close()
            if selected == self.current_chat:
                self.current_chat = None
                self.set_disabled_input()

    def send_message(self):
        message_text = self.main_ui.textEditMessage.toPlainText()
        self.main_ui.textEditMessage.clear()
        if not message_text:
            return
        try:
            self.transport.send_message(self.current_chat, message_text)
        except ServerError as err:
            self.messages.critical(self, 'Ошибка', err.text)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером!')
                self.close()
            self.messages.critical(self, 'Ошибка', 'Таймаут соединения!')
        except (ConnectionResetError, ConnectionAbortedError):
            self.messages.critical(self, 'Ошибка', 'Потеряно соединение с сервером!')
            self.close()
        else:
            self.database.save_message(self.current_chat, 'out', message_text)
            CLIENT_LOGGER.debug(f'Отправлено сообщение для {self.current_chat}: {message_text}')
            self.history_list_update()

    @pyqtSlot(str)
    def message(self, sender):
        """
        Обработка полученных сообщений
        :param sender:
        :return:
        """
        if sender == self.current_chat:
            self.history_list_update()
        else:
            if self.database.check_contact(sender):
                if self.messages.question(self, 'Новое сообщение',
                                          f'Получено новое сообщение от {sender}, '
                                          f'открыть чат с ним?', QMessageBox.Yes,
                                          QMessageBox.No) == QMessageBox.Yes:
                    self.current_chat = sender
                    self.set_active_user()
            else:
                print('NO')
                if self.messages.question(self, 'Новое сообщение',
                                          f'Получено новое сообщение от {sender}.\n '
                                          f'Данного пользователя нет в вашем контакт-листе.\n'
                                          f' Добавить в контакты и открыть чат с ним?',
                                          QMessageBox.Yes, QMessageBox.No) == QMessageBox.Yes:
                    self.add_contact(sender)
                    self.current_chat = sender
                    self.set_active_user()

    @pyqtSlot()
    def connection_lost(self):
        self.messages.warning(self, 'Сбой соединения', 'Потеряно соединение с сервером. ')
        self.close()

    def make_connection(self, trans_obj):
        trans_obj.new_message.connect(self.message)
        trans_obj.connection_lost.connect(self.connection_lost)

# Проверка функционирования стартового диалога
# ---------------------------------------------------------------------------
# if __name__ == '__main__':
#     app = QApplication([])
#     dial = StartDialog()
#     sys.exit(app.exec_())

# Проверка функционирования главного окна
# ---------------------------------------------------------------------------
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     path_db = os.path.abspath(os.path.join(os.path.dirname(__file__), './'))
#     database = ClientDB('test1', path_db)
#     from client_main import ClientTransport
#     transport = ClientTransport(7777, '127.0.0.1', database, 'test1')
#     window = ClientMainWindow(transport, database)
#     sys.exit(app.exec_())

# Проверка функционирования окна добавления контакта
# ---------------------------------------------------------------------------
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     import os
#     from client_db import ClientDB
#     path_db = os.path.abspath(os.path.join(os.path.dirname(__file__), './'))
#     database = ClientDB('test1', path_db)
#     from client_main import ClientTransport
#     transport = ClientTransport(7777, '127.0.0.1', database, 'test1')
#     window = AddContact(transport, database)
#     window.show()
#     sys.exit(app.exec_())

# Проверка функционирования окна удаления контакта
# ---------------------------------------------------------------------------
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     import os
#     from client_db import ClientDB
#     path_db = os.path.abspath(os.path.join(os.path.dirname(__file__), './'))
#     database = ClientDB('test1', path_db)
#     window = DelContact(database)
#     # при подключении контакты удаляются, а затем добавляются с сервера
#     # поэтому для проверки сами вручную добавляем контакт для списка удаления
#     database.add_contact('test1')
#     database.add_contact('test2')
#     print(database.get_contacts())
#     window.del_ui.comboBoxSelectUser.addItems(sorted(database.get_contacts()))
#     window.show()
#     sys.exit(app.exec_())
