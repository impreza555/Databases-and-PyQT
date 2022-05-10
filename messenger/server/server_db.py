import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, MetaData, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class ServerDB:
    """
    Класс - оболочка для работы с базой данных сервера.
    Использует SQLite базу данных, реализован с помощью
    SQLAlchemy ORM и используется декларативный подход.
    """
    PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
    PATH = os.path.join(PATH, 'server_db.db3')
    Base = declarative_base()

    class Users(Base):
        """Класс - отображение таблицы всех пользователей"""

        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        login = Column(String, unique=True)
        last_connection = Column(DateTime)
        passwd_hash = Column(String)
        pubkey = Column(Text)

        def __init__(self, login, passwd_hash):
            """
            Конструктор класса таблицы всех пользователей.
            :param login: str
            :param passwd_hash: str
            """
            self.login = login
            self.last_connection = datetime.datetime.now()
            self.passwd_hash = passwd_hash
            self.pubkey = None

    class ActiveUsers(Base):
        """Класс - отображение таблицы активных пользователей"""

        __tablename__ = 'active_users'
        id = Column(Integer, primary_key=True)
        user = Column(String, ForeignKey('users.id'), unique=True)
        ip = Column(String)
        port = Column(Integer)
        time_connection = Column(DateTime)

        def __init__(self, user, ip, port, time_connection):
            """
            Конструктор класса таблицы активных пользователей.
            :param user: str
            :param ip: str
            :param port: int
            :param time_connection: datetime
            """
            self.user = user
            self.ip = ip
            self.port = port
            self.time_connection = time_connection

    class LoginHistory(Base):
        """Класс - отображение таблицы истории входов пользователей"""

        __tablename__ = 'login_history'
        id = Column(Integer, primary_key=True)
        user = Column(String, ForeignKey('users.id'))
        date_time = Column(DateTime)
        ip = Column(String)
        port = Column(Integer)

        def __init__(self, user, date, ip, port):
            """
            Конструктор класса таблицы истории входов пользователей.
            :param user: str
            :param date: datetime
            :param ip: str
            :param port: int
            """
            self.user = user
            self.date_time = date
            self.ip = ip
            self.port = port

    class UsersContacts(Base):
        """Класс - отображение таблицы контактов пользователей"""

        __tablename__ = 'users_contacts'
        id = Column(Integer, primary_key=True)
        user = Column(String, ForeignKey('users.id'))
        contact = Column(String, ForeignKey('users.id'))

        def __init__(self, user, contact):
            """
            Конструктор класса таблицы контактов пользователей.
            :param user: str
            :param contact: str
            """
            self.user = user
            self.contact = contact

    class UsersHistory(Base):
        """Класс - отображение таблицы истории действий пользователей"""

        __tablename__ = 'users_history'
        id = Column(Integer, primary_key=True)
        user = Column(String, ForeignKey('users.id'))
        sent = Column(Integer)
        accepted = Column(Integer)

        def __init__(self, user):
            """
            Конструктор класса истории действий пользователей.
            :param user: str
            """
            self.user = user
            self.sent = 0
            self.accepted = 0

    def __init__(self, path=PATH):
        """
        Конструктор класса базы данных.
        :param path: str
        """
        self.engine = create_engine(f'sqlite:///{path}', echo=False, pool_recycle=7200,
                                    connect_args={'check_same_thread': False})
        self.metadata = MetaData()
        self.Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip_address, port, key):
        """
        Метод выполняющийся при входе пользователя, записывает в базу факт входа
        обновляет открытый ключ пользователя при его изменении.
        :param username: str
        :param ip_address: str
        :param port: int
        :param key: str
        :return: None
        """
        query = self.session.query(self.Users).filter_by(login=username)
        if query.count():
            user = query.first()
            user.last_connection = datetime.datetime.now()
            if user.pubkey != key:
                user.pubkey = key
        else:
            raise ValueError('Пользователь не зарегистрирован.')
        new_active_user = self.ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)
        history = self.LoginHistory(user.id, datetime.datetime.now(), ip_address, port)
        self.session.add(history)
        self.session.commit()

    def add_user(self, name, passwd_hash):
        """
        Метод регистрации пользователя.
        Принимает имя и хэш пароля, создаёт запись в таблице статистики.
        :param name: str
        :param passwd_hash: str
        :return: None
        """
        user_row = self.Users(name, passwd_hash)
        self.session.add(user_row)
        self.session.commit()
        history_row = self.UsersHistory(user_row.id)
        self.session.add(history_row)
        self.session.commit()

    def remove_user(self, name):
        """Метод удаляющий пользователя из базы.
        :param name: str
        :return: None
        """
        user = self.session.query(self.Users).filter_by(login=name).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.query(self.LoginHistory).filter_by(user=user.id).delete()
        self.session.query(self.UsersContacts).filter_by(user=user.id).delete()
        self.session.query(self.UsersContacts).filter_by(contact=user.id).delete()
        self.session.query(self.UsersHistory).filter_by(user=user.id).delete()
        self.session.query(self.Users).filter_by(login=name).delete()
        self.session.commit()

    def get_hash(self, name):
        """Метод получения хеша пароля пользователя.
        :param name: str
        :return: str
        """
        user = self.session.query(self.Users).filter_by(login=name).first()
        return user.passwd_hash

    def get_pubkey(self, name):
        """Метод получения публичного ключа пользователя.
        :param name: str
        :return: str
        """
        user = self.session.query(self.Users).filter_by(login=name).first()
        return user.pubkey

    def check_user(self, name):
        """Метод проверяющий существование пользователя.
        :param name: str
        :return: bool
        """
        if self.session.query(self.Users).filter_by(login=name).count():
            return True
        else:
            return False

    def user_logout(self, username):
        """
        Метод выполняющийся при выходе пользователя, записывает в базу факт выхода.
        :param username: str
        :return: None
        """
        user = self.session.query(self.Users).filter_by(login=username).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def users_list(self):
        """
        Метод возвращающий список известных пользователей со временем последнего входа.
        :return: list
        """
        query = self.session.query(
            self.Users.login,
            self.Users.last_connection,
        )
        return query.all()

    def active_users_list(self):
        """
        Метод возвращающий список активных пользователей.
        :return: list
        """
        query = self.session.query(self.Users.login,
                                   self.ActiveUsers.ip,
                                   self.ActiveUsers.port,
                                   self.ActiveUsers.time_connection
                                   ).join(self.Users)
        return query.all()

    def login_history(self, username=None):
        """
        Метод возвращающий историю входов.
        :param username: str
        :return: list
        """
        query = self.session.query(self.Users.login,
                                   self.LoginHistory.date_time,
                                   self.LoginHistory.ip,
                                   self.LoginHistory.port
                                   ).join(self.Users)
        if username:
            query = query.filter(self.Users.login == username)
        return query.all()

    def process_message(self, sender, recipient):
        """
        Метод записывающий в таблицу статистики факт передачи сообщения.
        :param sender: str
        :param recipient: str
        :return: None
        """
        sender = self.session.query(self.Users).filter_by(login=sender).first().id
        recipient = self.session.query(self.Users).filter_by(login=recipient).first().id
        sender_row = self.session.query(self.UsersHistory).filter_by(user=sender).first()
        sender_row.sent += 1
        recipient_row = self.session.query(self.UsersHistory).filter_by(user=recipient).first()
        recipient_row.accepted += 1
        self.session.commit()

    def get_contacts(self, username):
        """
        Метод возвращающий список контактов пользователя.
        :param username: str
        :return: list
        """
        user = self.session.query(self.Users).filter_by(login=username).one()
        query = self.session.query(
            self.UsersContacts,
            self.Users.login
        ).filter_by(user=user.id).join(
            self.Users,
            self.UsersContacts.contact == self.Users.id
        )
        return [contact[1] for contact in query.all()]

    def add_contact(self, user, contact):
        """
        Метод добавления контакта для пользователя.
        :param user: str
        :param contact: str
        :return: None
        """
        user = self.session.query(self.Users).filter_by(login=user).first()
        contact = self.session.query(self.Users).filter_by(login=contact).first()
        if not contact or self.session.query(
                self.UsersContacts).filter_by(user=user.id,
                                              contact=contact.id).count():
            return
        contact_row = self.UsersContacts(user.id, contact.id)
        self.session.add(contact_row)
        self.session.commit()

    def remove_contact(self, user, contact):
        """
        Метод удаления контакта пользователя.
        :param user: str
        :param contact: str
        :return: None
        """
        user = self.session.query(self.Users).filter_by(login=user).first()
        contact = self.session.query(self.Users).filter_by(login=contact).first()
        if not contact:
            return
        self.session.query(self.UsersContacts).filter(
            self.UsersContacts.user == user.id,
            self.UsersContacts.contact == contact.id
        ).delete()
        self.session.commit()

    def message_history(self):
        """
        Метод возвращающий статистику сообщений.
        :return: list
        """
        query = self.session.query(self.Users.login,
                                   self.Users.last_connection,
                                   self.UsersHistory.sent,
                                   self.UsersHistory.accepted
                                   ).join(self.Users)
        return query.all()

# # TODO: допилить потом отладку для феншуя.
# if __name__ == '__main__':
#     db = ServerDB('test.db3')
#     db.user_login('Вася', '192.168.1.4', 8888, 'блаблабла')
#     db.user_login('Зина', '192.168.1.5', 7777, 'блаблаблабла')
#     print(db.users_list())
#     print(db.active_users_list())
#     db.user_logout('Вася')
#     print(db.users_list())
#     print(db.active_users_list())
#     db.user_logout('Зина')
#     print(db.users_list())
#     print(db.active_users_list())
#     print(db.login_history('Вася'))
#     db.add_contact('test2', 'test1')
#     db.add_contact('test1', 'test3')
#     db.add_contact('test1', 'test6')
#     db.remove_contact('test1', 'test3')
#     print(db.users_list())
#     db.process_message('Зина', 'Вася')
#     print(db.message_history())
