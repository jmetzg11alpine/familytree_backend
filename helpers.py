from models import Person, Photo
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError
import os
import base64
from datetime import datetime


def update_coor_range(x, y, coor_range):
    if x < coor_range['minX']:
        coor_range['minX'] = x
    if x > coor_range['maxX']:
        coor_range['maxX'] = x
    if y < coor_range['minY']:
        coor_range['minY'] = y
    if y > coor_range['maxY']:
        coor_range['maxY'] = y
    return coor_range


def get_all_people(db):
    people = db.query(Person).all()
    name_key, coor_key = {}, {}
    coor_range = {'minY': float('inf'), 'maxY': -float('inf'), 'minX': float('inf'), 'maxX': -float('inf')}
    for p in people:
        x, y = p.x, p.y
        coor = str(x) + '<>' + str(y)
        coor_key[coor] = p.id
        name_key[p.id] = p.name
        coor_range = update_coor_range(x, y, coor_range)
    coor_range['minX'] -= 3
    coor_range['maxX'] += 3
    coor_range['minY'] -= 3
    coor_range['maxY'] += 3
    return name_key, coor_key, coor_range


def get_name(db, id):
    try:
        person = db.query(Person).filter(Person.id == id).first()
        return person.name
    except AttributeError:
        return None


def get_id(db, name):
    try:
        person = db.query(Person).filter(Person.name == name).first()
        return person.id
    except AttributeError:
        return None


def process_relationships(db, relationship_string):
    if type(relationship_string) is str:
        relatationship_list = []
        relationships = relationship_string.split(',')
        for relation in relationships:
            relatationship_list.append(get_name(db, relation))
    else:
        relatationship_list = None
    return relatationship_list


def get_bio(name):
    bio_file_path = os.path.join('BIOS', name) + '.txt'
    if not os.path.exists(bio_file_path) or not os.path.isfile(bio_file_path):
        return None
    else:
        with open(bio_file_path, 'r') as file:
            bio_content = file.read()
        return bio_content


def get_profile_photo(db, id):
    photo = db.query(Photo).filter(Photo.person_id == id, Photo.profile_photo == 1).first()
    if photo:
        path = photo.path
    else:
        path = 'PHOTOS/default_photo.png'
    with open(path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def check_null_list(value_list):
    if not value_list or not value_list[0]:
        return None
    else:
        return value_list


def get_person_details(db, id):
    person = db.query(Person).filter(Person.id == id).first()
    parents_list = process_relationships(db, person.parents)
    spouse_list = process_relationships(db, person.spouse)
    children_list = process_relationships(db, person.children)
    siblings_list = process_relationships(db, person.siblings)
    bio = get_bio(person.name)
    profile_photo = get_profile_photo(db, id)
    return {'name': person.name, 'birth': person.birth, 'location': person.location, 'parents': check_null_list(parents_list),
            'children': check_null_list(children_list), 'spouse': check_null_list(spouse_list), 'siblings': check_null_list(siblings_list),
            'bio': bio, 'profile_photo': profile_photo}


def search_potential_relatives(minX, maxX, minY, maxY, db):
    people = db.query(Person).filter(and_(
        Person.x > minX,
        Person.x < maxX,
        Person.y > minY,
        Person.y < maxY
    ))
    return [{'id': person.id, 'name': person.name} for person in people]


def find_parents(x, y, db):
    return search_potential_relatives(x-6, x+6, y-4, y, db)


def find_siblings(x, y, db):
    return search_potential_relatives(x-6, x+6, y-2, y+2, db)


def find_children(x, y, db):
    return search_potential_relatives(x-6, x+6, y, y+4, db)


def find_spouses(x, y, db):
    return search_potential_relatives(x-2, x+2, y-2, y+2, db)


def find_potential_relatives(db, coor):
    coor = coor.split('<>')
    x, y = int(coor[0]), int(coor[1])
    parents = find_parents(x, y, db)
    siblings = find_siblings(x, y, db)
    children = find_children(x, y, db)
    spouses = find_spouses(x, y, db)
    return {'parents': parents, 'siblings': siblings, 'children': children, 'spouses': spouses}


def update_person_field(db, person_id, field, new_person_id):
    new_person_id = str(new_person_id)
    person = db.query(Person).filter_by(id=person_id).first()
    if person:
        existing_ids = getattr(person, field, None)
        if existing_ids:
            updated_ids = existing_ids + ',' + new_person_id
        else:
            updated_ids = new_person_id
        setattr(person, field, updated_ids)


def update_related_persons(db, new_person_id, data):
    for relation in ['siblings', 'children', 'parents', 'spouse']:
        if relation in data:
            for relative_id in data[relation].split(','):
                if relation == 'children':
                    update_person_field(db, relative_id, 'parents', str(new_person_id))
                elif relation == 'parents':
                    update_person_field(db, relative_id, 'children', str(new_person_id))
                elif relation == 'siblings':
                    update_person_field(db, relative_id, 'siblings', str(new_person_id))
                else:
                    update_person_field(db, relative_id, 'spouse', str(new_person_id))


def add_new_relative(formData, squareCoor, db):
    data = {}
    coor = squareCoor.split('<>')
    x, y = coor[0], coor[1]
    data['x'], data['y'] = x, y
    for info in formData['fields']:
        if info['label'] == 'Name':
            data['name'] = info['value']
        elif info['label'] == 'Location':
            data['location'] = info['value']
        elif info['label'] == 'Birthday':
            if (info['value']):
                birth = datetime.strptime(info['value'], '%Y-%m-%d').date()
                data['birth'] = birth
        elif info['label'] == 'Parents':
            parent_ids = ','.join([str(get_id(db, person)) for person in info['value']])
            data['parents'] = parent_ids
        elif info['label'] == 'Siblings':
            sibling_ids = ','.join([str(get_id(db, person)) for person in info['value']])
            data['siblings'] = sibling_ids
        elif info['label'] == 'Children':
            children_ids = ','.join([str(get_id(db, person)) for person in info['value']])
            data['children'] = children_ids
        elif info['label'] == 'Spouse':
            spouse_ids = ','.join([str(get_id(db, person)) for person in info['value']])
            data['spouse'] = spouse_ids

    try:
        person = Person(**data)
        db.add(person)
        db.commit()
        new_person_id = person.id
        update_related_persons(db, new_person_id, data)
        db.commit()
        message = 'success'
    except IntegrityError:
        db.rollback()
        message = 'error'
    name = data['name']
    return message, name
