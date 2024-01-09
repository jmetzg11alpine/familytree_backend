from database import SessionLocal, engine
from models import Person, Photo, User, History, Visitor, Base
import random
import datetime
import os


def clear_bios():
    bios_dir = './BIOS'
    for filename in os.listdir(bios_dir):
        file_path = os.path.join(bios_dir, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)


def clear_photos():
    photo_dir = './PHOTOS'
    for person_id in os.listdir(photo_dir):
        person_id_path = os.path.join(photo_dir, person_id)
        if os.path.isdir(person_id_path):
            for filename in os.listdir(person_id_path):
                file_path = os.path.join(person_id_path, filename)
                os.unlink(file_path)


def make_ip_address():
    return '.'.join(str(random.randint(0, 255)) for _ in range(4))


def get_time_values():
    start_date = datetime.date(2022, 11, 1)
    end_date = datetime.date(2024, 1, 6)
    delta = datetime.timedelta(days=1)
    return start_date, end_date, delta


def make_visitor_data(session):
    current_date, end_date, date_delta = get_time_values()
    while current_date <= end_date:
        random_number = random.randint(1, 5)
        for _ in range(random_number):
            ip_address = make_ip_address()
            visitor = Visitor(ip_address=ip_address, date=current_date)
            session.add(visitor)
        current_date += date_delta


def recreate_tables():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def populate_database():
    recreate_tables()
    session = SessionLocal()

    session.query(Person).delete()
    session.query(Photo).delete()
    session.query(History).delete()

    people_list = [
        {'id': 1, 'name': 'Jesse Metzger', 'x': 20, 'y': 21, 'birth': datetime.date(
            1989, 1, 17), 'location': 'Nashville ,TN', 'parents': '3,5', 'spouse': '2', 'siblings': '4',
            'lat': 36.1627, 'lng': -86.7816},
        {'id': 2, 'name': 'Ellina Metzger', 'x': 21, 'y': 21, 'birth': datetime.date(
            1991, 5, 5), 'location': 'Nashville, TN', 'parents': '7,8', 'spouse': '1', 'siblings': '6',
            'lat': 36.1627, 'lng': -86.7816},
        {'id': 3, 'name': 'Helen Metzger', 'x': 18, 'y': 19, 'birth': datetime.date(
            1959, 1, 13), 'location': 'San Diego, CA', 'spouse': '5', 'children': '1,4',
            'lat': 32.8351, 'lng': -116.7664},
        {'id': 4, 'name': 'Jennifer Metzger', 'x': 17, 'y': 21, 'birth': datetime.date(
            1991, 11, 15), 'location': 'Las Vegas, NV', 'parents': '3,5', 'siblings': '1',
            'lat': 36.1716, 'lng': -115.1891},
        {'id': 5, 'name': 'James Metzger', 'x': 19, 'y': 19, 'birth': datetime.date(
            1957, 4, 10), 'location': 'San Diego, CA', 'spouse': '3', 'children': '1,4',
            'lat': 32.8351, 'lng': -116.7664},
        {'id': 6, 'name': 'Polina Volkova', 'x': 24, 'y': 21, 'birth': datetime.date(
            1996, 1, 16), 'location': 'Moscow, Russia', 'parents': '7,8', 'siblings': '2',
            'lat': 55.7558, 'lng': 37.6173},
        {'id': 7, 'name': 'Anna Volkova', 'x': 22, 'y': 19, 'birth': datetime.date(
            1968, 10, 12), 'location': 'Moscow, Russia', 'spouse': '8', 'children': '2,6',
            'lat': 55.7558, 'lng': 37.6173},
        {'id': 8, 'name': 'Yuriy Volkov', 'x': 23, 'y': 19, 'birth': datetime.date(
            1966, 8, 18), 'location': 'Moscow, Russia', 'spouse': '7', 'children': '2,6',
            'lat': 55.7558, 'lng': 37.6173},
        {'id': 9, 'name': 'Mioyko Jones', 'x': 17, 'y': 17, 'birth': datetime.date(
            1910, 2, 2), 'location': 'San Diego', 'spouse': '10', 'children': '3',
            'lat': 32.7448, 'lng': -116.9989},
        {'id': 10, 'name': 'Howard Jones', 'x': 16, 'y': 17, 'birth': datetime.date(
            1910, 4, 4), 'location': 'San Diego', 'spouse': '9', 'children': '3',
            'lat': 32.7448, 'lng': -116.9989}
    ]

    user_list = [
        {'username': 'Helen Metzger', 'password': 'mother'},
        {'username': 'Jesse Metzger', 'password': 'jesse'},
        {'username': 'Jennifer Metzger', 'password': 'sister'},
        {'username': 'Ellina Metzger', 'password': 'wife'}
    ]

    try:
        for data in people_list:
            person = Person(**data)
            session.add(person)
        for data in user_list:
            user = User(**data)
            session.add(user)
        history = History(username='Jesse Metzger', action='Project Started', recipient='General')
        session.add(history)

        clear_bios()
        clear_photos()
        ###### fills Visitor table for development purposes #########
        # make_visitor_data(session)

        session.commit()
        print('Default data inserted')
    except Exception as e:
        session.rollback()
        print(f'Error: {e}')
    finally:
        session.close()


if __name__ == '__main__':
    populate_database()
