from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from users import add_users
from foreign_aid import update_foreign_aid
from budget import update_budget
from health import update_health
from logistics import update_logistics
from urllib.parse import quote_plus
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv()

from database import Base


def start_session_and_create_schemas():
    PASSWORD = os.getenv('DATABASE_PASSWORD')
    DATABASE_URL = os.getenv('DATABASE_URL')

    safe_password = quote_plus(PASSWORD)
    complete_url = DATABASE_URL.replace('<password>', safe_password)
    engine = create_engine(complete_url)

    # creates table
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    return session


if __name__ == '__main__':
    session = start_session_and_create_schemas()
    # users aren't saved in the backup. They can be manually added here
    if len(sys.argv) > 1 and sys.argv[1] == 'users':
        add_users(session)
    elif len(sys.argv) > 1 and sys.argv[1] == 'foreign_aid':
        update_foreign_aid(session)
    elif len(sys.argv) > 1 and sys.argv[1] == 'budget':
        update_budget(session)
    elif len(sys.argv) > 1 and sys.argv[1] == 'health':
        update_health(session)
    elif len(sys.argv) > 1 and sys.argv[1] == 'logistics':
        update_logistics(session)
    elif len(sys.argv) > 1 and sys.argv[1] == 'all':
        add_users(session)
        update_foreign_aid(session)
        update_budget(session)
        update_health(session)
        update_logistics(session)
    else:
        print('add argument: budget, foreign_aid, users, health, logistics or all')
    session.close()
