import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class ServerDB:
    PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
    PATH = os.path.join(PATH, 'server_db.db3')
    Base = declarative_base()

    class Users(Base):
        __tablename__ = 'users'
        id = Column(Integer, primary_key=True)
        login = Column(String, unique=True)
        last_connection = Column(DateTime)

        def __init__(self, login):
            self.login = login
            self.last_connection = datetime.datetime.now()

    class ActiveUsers(Base):
        __tablename__ = 'active_users'
        id = Column(Integer, primary_key=True)
        user = Column(String, ForeignKey('users.id'), unique=True)
        ip = Column(String)
        port = Column(Integer)
        time_connection = Column(DateTime)

        def __init__(self, user, ip, port, time_connection):
            self.user = user
            self.ip = ip
            self.port = port
            self.time_connection = time_connection

    class LoginHistory(Base):
        __tablename__ = 'login_history'
        id = Column(Integer, primary_key=True)
        user = Column(String, ForeignKey('users.id'))
        ip = Column(String)
        port = Column(Integer)
        last_connection = Column(DateTime)

        def __init__(self, user, ip, port, last_connection):
            self.user = user
            self.ip = ip
            self.port = port
            self.last_connection = last_connection

    class UsersContacts(Base):
        __tablename__ = 'users_contacts'
        id = Column(Integer, primary_key=True)
        user = Column(String, ForeignKey('users.id'))
        contact = Column(String, ForeignKey('users.id'))

        def __init__(self, user, contact):
            self.user = user
            self.contact = contact

    class UsersHistory(Base):
        __tablename__ = 'users_history'
        id = Column(Integer, primary_key=True)
        user = Column(String, ForeignKey('users.id'))
        sent = Column(Integer)
        accepted = Column(Integer)

        def __init__(self, user):
            self.user = user
            self.sent = 0
            self.accepted = 0

    def __init__(self, path=PATH):
        self.engine = create_engine(f'sqlite:///{path}', echo=False, pool_recycle=7200,
                                    connect_args={'check_same_thread': False})
        self.metadata = MetaData()
        self.Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        self.session.query(self.ActiveUsers).delete()
        self.session.commit()

    def user_login(self, username, ip_address, port):
        query = self.session.query(self.Users).filter_by(login=username)
        if query.count():
            user = query.first()
            user.last_connection = datetime.datetime.now()
        else:
            user = self.Users(username)
            self.session.add(user)
            self.session.commit()
            user_in_history = self.UsersHistory(user.id)
            self.session.add(user_in_history)
        new_active_user = self.ActiveUsers(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(new_active_user)
        history = self.LoginHistory(user.id, ip_address, port, datetime.datetime.now())
        self.session.add(history)
        self.session.commit()

    def user_logout(self, username):
        user = self.session.query(self.Users).filter_by(login=username).first()
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    def users_list(self):
        query = self.session.query(
            self.Users.login,
            self.Users.last_connection,
        )
        return query.all()

    def active_users_list(self):
        query = self.session.query(self.Users.login,
                                   self.ActiveUsers.ip,
                                   self.ActiveUsers.port,
                                   self.ActiveUsers.time_connection
                                   ).join(self.Users)
        return query.all()

    def login_history(self, username=None):
        query = self.session.query(self.Users.login,
                                   self.LoginHistory.last_connection,
                                   self.LoginHistory.ip,
                                   self.LoginHistory.port
                                   ).join(self.Users)
        if username:
            query = query.filter(self.Users.login == username)
        return query.all()

    def process_message(self, sender, recipient):
        sender = self.session.query(self.Users).filter_by(login=sender).first().id
        recipient = self.session.query(self.Users).filter_by(login=recipient).first().id
        sender_row = self.session.query(self.UsersHistory).filter_by(user=sender).first()
        sender_row.sent += 1
        recipient_row = self.session.query(self.UsersHistory).filter_by(user=recipient).first()
        recipient_row.accepted += 1
        self.session.commit()

    def get_contacts(self, username):
        user = self.session.query(self.Users).filter_by(login=username).one()
        query = self.session.query(self.UsersContacts, self.Users.login
                                   ).filter_by(user=user.id
                                               ).join(self.Users,
                                                      self.UsersContacts.contact == self.Users.id)
        return [contact[1] for contact in query.all()]

    def add_contact(self, user, contact):
        user = self.session.query(self.Users).filter_by(login=user).first()
        contact = self.session.query(self.Users).filter_by(login=contact).first()
        if not contact or self.session.query(self.UsersContacts
                                             ).filter_by(user=user.id, contact=contact.id
                                                         ).count():
            return
        contact_row = self.UsersContacts(user.id, contact.id)
        self.session.add(contact_row)
        self.session.commit()

    def remove_contact(self, user, contact):
        user = self.session.query(self.Users).filter_by(login=user).first()
        contact = self.session.query(self.Users).filter_by(login=contact).first()
        if not contact:
            return
        print(self.session.query(self.UsersContacts
                                 ).filter(self.UsersContacts.user == user.id,
                                          self.UsersContacts.contact == contact.id
                                          ).delete())
        self.session.commit()

    def message_history(self):
        query = self.session.query(self.Users.login,
                                   self.Users.last_connection,
                                   self.UsersHistory.sent,
                                   self.UsersHistory.accepted
                                   ).join(self.Users)
        return query.all()


if __name__ == '__main__':
    db = ServerDB('test.db3')
    db.user_login('Вася', '192.168.1.4', 8888)
    db.user_login('Зина', '192.168.1.5', 7777)
    print(db.users_list())
    print(db.active_users_list())
    db.user_logout('Вася')
    print(db.users_list())
    print(db.active_users_list())
    db.user_logout('Зина')
    print(db.users_list())
    print(db.active_users_list())
    print(db.login_history('Вася'))
    db.add_contact('test2', 'test1')
    db.add_contact('test1', 'test3')
    db.add_contact('test1', 'test6')
    db.remove_contact('test1', 'test3')
    print(db.users_list())
    db.process_message('Зина', 'Вася')
    print(db.message_history())
