from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os

PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
PATH = os.path.join(PATH, 'server_db.db3')


class ServerDB:
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

    def __init__(self):
        self.engine = create_engine(f'sqlite:///{PATH}', echo=False, pool_recycle=7200)

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


if __name__ == '__main__':
    db = ServerDB()
    db.user_login('Вася', '192.168.1.4', 8888)
    db.user_login('Зина', '192.168.1.5', 7777)
    print(db.active_users_list())
    db.user_logout('Вася')
    print(db.users_list())
    print(db.active_users_list())
    db.user_logout('Зина')
    print(db.users_list())
    print(db.active_users_list())
