from sqlalchemy import Column, Boolean, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(Date, default=func.now())
    name = Column(String(255), unique=True)
    x = Column(Integer())
    y = Column(Integer())
    birth = Column(Date)
    location = Column(String(255))
    parents = Column(String(10))
    spouse = Column(String(10))
    siblings = Column(String(20))
    children = Column(String(20))


class Photo(Base):
    __tablename__ = 'photo'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    person_id = Column(Integer)
    profile_photo = Column(Boolean)
    path = Column(String(100))
