from sqlalchemy import Column, Integer, Float, String, DateTime, CheckConstraint
from database import Base


class Health(Base):
    __tablename__ = 'health'
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    pressure = Column(String(10), nullable=False)
    weight = Column(Float, CheckConstraint('weight < 1000.0'), nullable=False)
    heart_beat = Column(Integer, CheckConstraint('heart_beat < 1000'), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    coffee = Column(Integer, CheckConstraint('coffee < 100'), nullable=False)
    notes = Column(String(255), nullable=True)
