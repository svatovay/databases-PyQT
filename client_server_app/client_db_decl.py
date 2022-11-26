from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime


class ClientDB:
    Base = declarative_base()

    class Client(Base):
        __tablename__ = 'clients'

        id = Column(Integer, primary_key=True)
        login = Column(String, unique=True)
        info = Column(String)

        def __init__(self, login, info):
            self.login = login
            self.info = info

    class ClientStory(Base):
        __tablename__ = 'clients_story'

        id = Column(Integer, primary_key=True)
        entry_time = Column(DateTime)
        ip_address = Column(String)

        def __init__(self, entry_time, ip_address):
            self.entry_time = entry_time
            self.ip_address = ip_address

    class ContactList(Base):
        __tablename__ = 'contacts_list'

        id = Column(Integer, primary_key=True)
        owner_id = Column(Integer)
        client_id = Column(Integer, ForeignKey('clients.id'))

        def __init__(self, owner_id, client_id):
            self.client_id = client_id
            self.owner_id = owner_id

    def __init__(self):
        self.engine = create_engine('sqlite:///client_base.db3', echo=False, pool_recycle=7200)

        self.Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

        self.session.commit()


if __name__ == '__main__':
    db = ClientDB()
