from urllib.parse import quote
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base
import os
from dotenv import load_dotenv
load_dotenv()

password = os.getenv('DATABASE_PASSWORD')
password_quoted = quote(password.encode('utf-8'))
DATABASE_URL = os.getenv('DATABASE_URL').replace("<password>", password_quoted)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
