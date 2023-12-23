from urllib.parse import quote
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

password = quote("P@ssw0rd")

DATABASE_URL = f"mysql+mysqlconnector://root:{password}@localhost/seemyfamily"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
