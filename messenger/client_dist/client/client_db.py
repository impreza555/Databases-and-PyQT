import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, MetaData, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class ClientDB:
    """
    Класс - оболочка для работы с базой данных клиента.
    Использует SQLite базу данных, реализован с помощью
    SQLAlchemy ORM и используется декларативный подход.
    """
    Base = declarative_base()

    class KnownUsers(Base):
        """
        Класс - отображение для таблицы всех пользователей.
        """
        __tablename__ = 'known_users'
        id = Column(Integer, primary_key=True)
        username = Column(String)

        def __init__(self, user):
            """
            Конструктор класса таблицы всех пользователей.
            :param user: str
            """
            self.username = user

    class MessageStat(Base):
        """
        Класс - отображение для таблицы статистики переданных сообщений.
        """
        __tablename__ = 'message_history'
        id = Column(Integer, primary_key=True)
        contact = Column(String)
        direction = Column(String)
        message = Column(Text)
        date = Column(DateTime)

        def __init__(self, contact, direction, message):
            """
            Конструктор класса таблицы статистики переданных сообщений.
            :param contact: str
            :param direction: str
            :param message: str
            """
            self.contact = contact
            self.direction = direction
            self.message = message
            self.date = datetime.datetime.now()

    class Contacts(Base):
        """
        Класс - отображение для таблицы контактов.
        """
        __tablename__ = 'contacts'
        id = Column(Integer, primary_key=True)
        name = Column(String, unique=True)

        def __init__(self, contact):
            """
            Конструктор класса таблицы контактов.
            :param contact: str
            """
            self.name = contact

    def __init__(self, name, path):
        """
        Конструктор класса базы данных.
        :param name: str
        :param path: str
        """
        self.path = path
        self.path = os.path.join(self.path, f'client_db_{name}.db3')
        self.engine = create_engine(f'sqlite:///{self.path}',
                                    echo=False,
                                    pool_recycle=7200,
                                    connect_args={'check_same_thread': False})
        self.metadata = MetaData()
        self.Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.session.query(self.Contacts).delete()
        self.session.commit()

    def add_contact(self, contact):
        """
        Метод добавляющий контакт в базу данных.
        :param contact: str
        :return: None
        """
        if not self.session.query(self.Contacts).filter_by(name=contact).count():
            contact_row = self.Contacts(contact)
            self.session.add(contact_row)
            self.session.commit()

    def del_contact(self, contact):
        """
        Метод, удаляющий определённый контакт.
        :param contact: str
        :return: None
        """
        self.session.query(self.Contacts).filter_by(name=contact).delete()
        self.session.commit()

    def contacts_clear(self):
        """ Метод, очищающий таблицу со списком контактов.
        :return: None
        """
        self.session.query(self.Contacts).delete()
        self.session.commit()

    def add_users(self, users_list):
        """
        Метод, заполняющий таблицу известных пользователей.
        :param users_list: list
        :return: None
        """
        self.session.query(self.KnownUsers).delete()
        for user in users_list:
            user_row = self.KnownUsers(user)
            self.session.add(user_row)
        self.session.commit()

    def save_message(self, contact, direction, message):
        """
        Метод, сохраняющий сообщение в базе данных.
        :param contact: str
        :param direction: str
        :param message: str
        :return: None
        """
        message_row = self.MessageStat(contact, direction, message)
        self.session.add(message_row)
        self.session.commit()

    def get_contacts(self):
        """
        Метод, возвращающий список всех контактов.
        :return: list
        """
        return [contact[0] for contact in self.session.query(self.Contacts.name).all()]

    def get_users(self):
        """
        Метод возвращающий список всех известных пользователей.
        :return: list
        """
        return [user[0] for user in self.session.query(self.KnownUsers.username).all()]

    def check_user(self, user):
        """
        Метод, проверяющий существует ли пользователь.
        :param user: str
        :return: bool
        """
        if self.session.query(self.KnownUsers).filter_by(username=user).count():
            return True
        else:
            return False

    def check_contact(self, contact):
        """
        Метод, проверяющий существует ли контакт.
        :param contact: str
        :return: bool
        """
        if self.session.query(self.Contacts).filter_by(name=contact).count():
            return True
        else:
            return False

    def get_history(self, contact):
        """
        Метод, возвращающий историю сообщений с определённым пользователем.
        :param contact: str
        :return: list
        """
        query = self.session.query(self.MessageStat).filter_by(contact=contact)
        return [(history_row.contact,
                 history_row.direction,
                 history_row.message,
                 history_row.date) for history_row in query.all()]


if __name__ == '__main__':
    path_db = os.path.abspath(os.path.join(os.path.dirname(__file__), '/'))
    db = ClientDB('test1', path_db)
    for i in ['test3', 'test4', 'test5']:
        db.add_contact(i)
    db.add_contact('test4')
    db.add_users(['test1', 'test2', 'test3', 'test4', 'test5'])
    db.save_message('test1', 'test2', f'Привет! я тестовое сообщение от {datetime.datetime.now()}!')
    db.save_message('test2', 'test1', f'Привет! я другое тестовое сообщение от {datetime.datetime.now()}!')
    print(db.get_contacts())
    print(db.get_users())
    print(db.check_user('test1'))
    print(db.check_user('test10'))
    print(sorted(db.get_history('test2'), key=lambda item: item[3]))
    db.del_contact('test4')
    print(db.get_contacts())
