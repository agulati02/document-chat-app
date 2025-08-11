from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from config.settings import USERS_TABLE


Base = declarative_base()

class User(Base):
    __tablename__ = USERS_TABLE

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
