from sqlalchemy import Column, Boolean, Integer, Float, String, Date, DateTime
from sqlalchemy.sql import func
from database import Base


# see my family
class Person(Base):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(Date, default=func.now())
    name = Column(String(255), unique=True)
    x = Column(Integer())
    y = Column(Integer())
    birth = Column(Date)
    location = Column(String(255))
    parents = Column(String(40))
    spouse = Column(String(40))
    siblings = Column(String(40))
    children = Column(String(40))
    lat = Column(Float, default=None)
    lng = Column(Float, default=None)


class Photo(Base):
    __tablename__ = 'photo'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    person_id = Column(Integer)
    profile_photo = Column(Boolean)
    path = Column(String(100))
    description = Column(String(255))


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100))
    password = Column(String(100))


class History(Base):
    __tablename__ = 'history'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=func.now())
    username = Column(String(100))
    action = Column(String(100))
    recipient = Column(String(100))


class Visitor(Base):
    __tablename__ = 'visitor'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ip_address = Column(String(225))
    date = Column(Date, default=func.now())
