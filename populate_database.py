from datetime import date
from database import SessionLocal, engine
from models import Person, Photo, Base
import os


def clear_bios():
    bios_dir = './BIOS'
    for filename in os.listdir(bios_dir):
        file_path = os.path.join(bios_dir, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)


def recreate_tables():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def populate_database():
    recreate_tables()
    session = SessionLocal()

    session.query(Person).delete()
    session.query(Photo).delete()

    people_list = [
        {'id': 1, 'name': 'Jesse Metzger', 'x': 20, 'y': 21, 'birth': date(
            1989, 1, 17), 'location': 'Nashville ,TN', 'parents': '3,5', 'spouse': '2', 'siblings': '4'},
        {'id': 2, 'name': 'Ellina Metzger', 'x': 21, 'y': 21, 'birth': date(
            1991, 5, 5), 'location': 'Nashville, TN', 'parents': '7,8', 'spouse': '1', 'siblings': '6'},
        {'id': 3, 'name': 'Helen Metzger', 'x': 18, 'y': 19, 'birth': date(
            1959, 1, 13), 'location': 'San Diego, CA', 'spouse': '5', 'children': '1,4'},
        {'id': 4, 'name': 'Jennifer Metzger', 'x': 17, 'y': 21, 'birth': date(
            1991, 11, 15), 'location': 'Las Vegas, NV', 'parents': '3,5', 'siblings': '1'},
        {'id': 5, 'name': 'James Metzger', 'x': 19, 'y': 19, 'birth': date(
            1957, 4, 10), 'location': 'San Diego, CA', 'spouse': '3', 'children': '1,4'},
        {'id': 6, 'name': 'Polina Volkova', 'x': 24, 'y': 21, 'birth': date(
            1996, 1, 16), 'location': 'Moscow, Russia', 'parents': '7,8', 'siblings': '2'},
        {'id': 7, 'name': 'Anna Volkova', 'x': 22, 'y': 19, 'birth': date(
            1968, 10, 12), 'location': 'Moscow, Russia', 'spouse': '8', 'children': '2,6'},
        {'id': 8, 'name': 'Yuriy Volkov', 'x': 23, 'y': 19, 'birth': date(
            1966, 8, 18), 'location': 'Moscow, Russia', 'spouse': '7', 'children': '2,6'},
        {'id': 9, 'name': 'Nobody One', 'x': 19, 'y': 16, 'birth': date(
            1922, 4, 22), 'location': 'Los Angeles', },
        {'id': 10, 'name': 'Nobody Two', 'x': 31, 'y': 25, 'birth': date(
            2002, 6, 11), 'location': 'Tijuana, Mexicor', }
    ]

    photo_list = [
        {'id': 1, 'person_id': 1, 'profile_photo': True, 'path': 'PHOTOS/1/one.png'},
        {'id': 2, 'person_id': 1, 'profile_photo': False, 'path': 'PHOTOS/1/two.png'},
        {'id': 3, 'person_id': 1, 'profile_photo': False, 'path': 'PHOTOS/1/three.png'},
        {'id': 4, 'person_id': 9, 'profile_photo': True, 'path': 'PHOTOS/9/nine.png'},
        {'id': 5, 'person_id': 10, 'profile_photo': True, 'path': 'PHOTOS/10/ten.png'},
    ]

    try:

        for data in people_list:
            person = Person(**data)
            session.add(person)
        for data in photo_list:
            photo = Photo(**data)
            session.add(photo)
        session.commit()

        print('Default data inserted')
    except Exception as e:
        session.rollback()
        print(f'Error: {e}')
    finally:
        session.close()

    clear_bios()


if __name__ == '__main__':
    populate_database()
