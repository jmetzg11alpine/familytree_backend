from sqlalchemy import Column, Integer, String, Float
from database import Base


class AgencyBudget(Base):
    __tablename__ = 'agency_budget'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    agency = Column(String(255))
    budget = Column(Float)


class ForeignAid(Base):
    __tablename__ = 'foreign_aid'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    country = Column(String(255))
    amount = Column(Float)
    year = Column(Integer)
    lat = Column(Float)
    lng = Column(Float)


class FunctionSpending(Base):
    __tablename__ = 'function_spending'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    year = Column(Integer)
    name = Column(String(255))
    amount = Column(Float)
