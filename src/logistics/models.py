from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from database import Base


class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    order_no = Column(String(10))
    start_location = Column(String(40))
    end_location = Column(String(40))
    miles = Column(Integer)
    units = Column(Integer)
    created_at = Column(DateTime)
    due_date = Column(DateTime)
    split = Column(Boolean)
    bus_id = Column(Integer, ForeignKey('bus.id'))
    finance_id = Column(Integer, ForeignKey('finance.id'))

    finance = relationship("Finance", back_populates='orders')
    bus = relationship("Bus", back_populates='orders')


class Bus(Base):
    __tablename__ = 'bus'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    units = Column(Integer)
    created_at = Column(DateTime)
    shipped = Column(DateTime)
    arrived = Column(DateTime)

    orders = relationship("Order", back_populates="bus")


class Finance(Base):
    __tablename__ = 'finance'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    driver_cost = Column(Integer)
    truck_cost = Column(Integer)
    payment_received = Column(Integer)
    sales_person = Column(String(50))
    customer = Column(String(120))

    orders = relationship("Order", back_populates="finance")
