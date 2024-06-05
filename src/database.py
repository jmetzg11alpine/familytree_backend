from urllib.parse import quote
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import time
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()


def connect_to_database(url, max_attempts=10, delay_seconds=3):
    for attempt in range(max_attempts):
        try:
            engine = create_engine(url)
            engine.connect()
            print('Database connection successful')
            return engine
        except Exception as e:
            print(f'--------------  Attempt {attempt + 1} fail. Retrying in {delay_seconds} seconds  ---------------------')
            print(e)
            time.sleep(delay_seconds)
    raise Exception('-----------------------  Failed to connect to the database after several attemps  ------------------------')


password = os.getenv('DATABASE_PASSWORD')
password_quoted = quote(password.encode('utf-8'))
DATABASE_URL = os.getenv('DATABASE_URL').replace("<password>", password_quoted)

engine = connect_to_database(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
