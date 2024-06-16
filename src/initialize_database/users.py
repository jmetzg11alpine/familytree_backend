import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.family_tree.models import User


def add_users(session):
    user_list = [
        {'username': 'Helen Metzger', 'password': os.getenv('HELEN')},
        {'username': 'Jesse Metzger', 'password': os.getenv('JESSE')},
        {'username': 'Jennifer Metzger', 'password': os.getenv('JENNIFER')},
        {'username': 'Ellina Metzger', 'password': os.getenv('ELLINA')}
    ]

    for user_info in user_list:
        existing_user = session.query(User).filter_by(username=user_info['username']).first()
        if existing_user is None:
            user = User(username=user_info['username'], password=user_info['password'])
            session.add(user)
        else:
            print(f"User {user_info['username']} already exists and was not added")

    session.commit()
    print("Database initialized and users added.")
