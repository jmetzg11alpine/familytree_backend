from models import Person, Photo
from sqlalchemy import and_, not_, or_
from sqlalchemy.exc import IntegrityError
import os
import base64
from datetime import datetime
import time
from collections import defaultdict


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
    return {'name': person.name, 'id': person.id, 'birth': person.birth, 'location': person.location, 'parents': check_null_list(parents_list),
            'children': check_null_list(children_list), 'spouse': check_null_list(spouse_list), 'siblings': check_null_list(siblings_list),
            'bio': bio, 'profile_photo': profile_photo, 'lat': person.lat, 'lng': person.lng}


def search_potential_relatives(minX, maxX, minY, maxY, db, id):
    people = db.query(Person).filter(and_(
        Person.x > minX,
        Person.x < maxX,
        Person.y > minY,
        Person.y < maxY
    ))
    return [{'id': person.id, 'name': person.name} for person in people if person.id != id]


def find_parents(x, y, db, id):
    return search_potential_relatives(x-8, x+8, y-4, y, db, id)


def find_siblings(x, y, db, id):
    return search_potential_relatives(x-8, x+8, y-2, y+2, db, id)


def find_children(x, y, db, id):
    return search_potential_relatives(x-8, x+8, y, y+4, db, id)


def find_spouses(x, y, db, id):
    return search_potential_relatives(x-4, x+4, y-2, y+2, db, id)


def find_potential_relatives(db, coor, id):
    coor = coor.split('<>')
    x, y = int(coor[0]), int(coor[1])
    parents = find_parents(x, y, db, id)
    siblings = find_siblings(x, y, db, id)
    children = find_children(x, y, db, id)
    spouses = find_spouses(x, y, db, id)
    return {'parents': parents, 'siblings': siblings, 'children': children, 'spouses': spouses}


def update_person_field(db, person_id, field, new_person_id):
    new_person_id = str(new_person_id)
    person = db.query(Person).filter_by(id=person_id).first()
    if person:
        existing_ids = getattr(person, field, None)
        if existing_ids and new_person_id not in existing_ids.split(','):
            updated_ids = existing_ids + ',' + new_person_id
        else:
            updated_ids = new_person_id
        setattr(person, field, updated_ids)


def update_related_persons(db, person_id, data):
    for relation in ['siblings', 'children', 'parents', 'spouse']:
        if relation in data and data[relation]:
            for relative_id in data[relation].split(','):
                if relation == 'children':
                    update_person_field(db, relative_id, 'parents', str(person_id))
                elif relation == 'parents':
                    update_person_field(db, relative_id, 'children', str(person_id))
                elif relation == 'siblings':
                    update_person_field(db, relative_id, 'siblings', str(person_id))
                else:
                    update_person_field(db, relative_id, 'spouse', str(person_id))


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
        elif info['label'] == 'Latitude':
            data['lat'] = info['value']
        elif info['label'] == 'Longitude':
            data['lng'] = info['value']
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


def get_values_and_options(person, db, field, potential_relatives, data):
    if field == 'spouses':
        ids = getattr(person, 'spouse')
    else:
        ids = getattr(person, field)
    if ids:
        ids_list = ids.split(',')
        values = [get_name(db, i) for i in ids_list]
    else:
        values = ''
    value_options = [person['name'] for person in potential_relatives[field]]
    data[field] = {'values': values, 'options': value_options}


def get_editable_details(id, db):
    person = db.query(Person).filter_by(id=id).first()
    if person:
        person_id = person.id
        x, y = str(person.x), str(person.y)
        potential_relatives = find_potential_relatives(db, x+'<>'+y, person_id)
        data = {}
        for field in ['parents', 'siblings', 'children', 'spouses']:
            get_values_and_options(person, db, field, potential_relatives, data)

        return {'fields': [
            {'label': 'Name', 'type': 'text', 'value': person.name, 'multiple': False},
            {'label': 'Birthday', 'type': 'date', 'value': person.birth, 'multiple': False},
            {'label': 'Location', 'type': 'text', 'value': person.location, 'multiple': False},
            {'label': 'Latitude', 'type': 'text', 'value': str(person.lat), 'multiple': False},
            {'label': 'Longitude', 'type': 'text', 'value': str(person.lng), 'multiple': False},
            {'label': 'Parents', 'options': data['parents']['options'], 'value': data['parents']['values'], 'multiple': True},
            {'label': 'Siblings', 'options': data['siblings']['options'], 'value': data['siblings']['values'], 'multiple': True},
            {'label': 'Children', 'options': data['children']['options'], 'value': data['children']['values'], 'multiple': True},
            {'label': 'Spouse', 'options': data['spouses']['options'], 'value': data['spouses']['values'], 'multiple': True}
            ]}
    else:
        return {}


def get_updated_data(data, db):
    values_with_list_key = {'Parents': 'parents', 'Siblings': 'siblings', 'Children': 'children', 'Spouse': 'spouse'}
    float_key = {'Latitude', 'Longitude'}
    new_data = {}
    for field in data['fields']:
        label = field['label']
        if label in values_with_list_key:
            value_names = set(field['value'])
            if value_names:
                values = [str(get_id(db, name)) for name in value_names]
                new_data[values_with_list_key[label]] = ','.join(values)
            else:
                new_data[values_with_list_key[label]] = None
        elif label in float_key:
            new_data[label] = float(field['value'])
        else:
            value = field['value']
            new_data[label] = value
    return new_data


def update_details(id, data, db):
    try:
        updated_data = get_updated_data(data, db)
        person = db.query(Person).filter_by(id=id).first()
        person_id = person.id
        update_related_persons(db, person_id, updated_data)
        person.name = updated_data['Name']
        person.birth = updated_data['Birthday']
        person.location = updated_data['Location']
        person.lat = updated_data['Latitude']
        person.lng = updated_data['Longitude']
        person.parents = updated_data['parents']
        person.spouse = updated_data['spouse']
        person.siblings = updated_data['siblings']
        person.children = updated_data['children']
        db.commit()
        message = 'success'
        name = updated_data['Name']
        return message, name
    except IntegrityError:
        db.rollback()
        message = 'error'
        name = updated_data['Name']
        return message, name


def remove_person(id_to_remove, ids, relation, db):
    if ids:
        for person_id in ids.split(','):
            person = db.query(Person).filter_by(id=int(person_id)).first()
            relation_ids = getattr(person, relation, '')
            new_relation_ids = [i for i in relation_ids.split(',') if int(i) != id_to_remove]
            setattr(person, relation, ','.join(new_relation_ids))


def remove_person_and_relations(name, db):
    person = db.query(Person).filter_by(name=name).first()
    person_id = person.id
    parents = person.parents
    remove_person(person_id, parents, 'children', db)
    spouse = person.spouse
    remove_person(person_id, spouse, 'spouse', db)
    siblings = person.siblings
    remove_person(person_id, siblings, 'siblings', db)
    children = person.children
    remove_person(person_id, children, 'parents', db)
    db.delete(person)
    db.commit()


def get_photos(person_id, db):
    photos = db.query(Photo).filter(Photo.person_id == person_id).all()
    data = {'current': '', 'description': ''}
    paths = []
    for photo in photos:
        if photo.profile_photo:
            with open(photo.path, 'rb') as image_file:
                data['current'] = base64.b64encode(image_file.read()).decode('utf-8')
            data['description'] = photo.description
        paths.append(photo.path)
    return data, paths


def get_photo(path, db):
    photo = db.query(Photo).filter(Photo.path == path).first()
    if photo:
        data = {}
        data['profile_photo'] = photo.profile_photo
        data['description'] = photo.description
        with open(photo.path, 'rb') as image_file:
            data['current'] = base64.b64encode(image_file.read()).decode('utf-8')
        return data
    else:
        return {'profile_photo': 0, 'description': '', 'current': ''}


def set_profile_photo(person_id, path, db):
    original_profile = db.query(Photo).filter(and_(Photo.person_id == person_id, Photo.profile_photo == 1)).first()
    new_profile = db.query(Photo).filter(and_(Photo.person_id == person_id, Photo.path == path)).first()
    original_profile.profile_photo = 0
    new_profile.profile_photo = 1
    db.commit()


def update_description_of_photo(description, path, db):
    photo = db.query(Photo).filter(Photo.path == path).first()
    photo.description = description
    db.commit()


def add_new_photo(photo_data, description, person_id, db):
    directory = f'PHOTOS/{str(person_id)}'
    if not os.path.exists(directory):
        os.makedirs(directory)
    path = directory + '/' + str(time.time()).split('.')[0] + '.png'
    with open(path, 'wb') as file:
        file.write(photo_data)
    person_has_photo = db.query(Photo).filter_by(person_id=person_id).first()
    profile_photo = 1 if person_has_photo is None else 0
    new_photo = Photo(person_id=person_id, profile_photo=profile_photo, path=path, description=description,)
    db.add(new_photo)
    db.commit()


def delete_one_photo(path, db):
    photo = db.query(Photo).filter_by(path=path).first()
    if photo:
        is_profile = photo.profile_photo
        person_id = photo.person_id
        if is_profile:
            new_profile_photo = db.query(Photo).filter_by(person_id=person_id).filter(Photo.id != photo.id).first()
            if new_profile_photo:
                new_profile_photo.profile_photo = True
                db.add(new_profile_photo)
        os.remove(path)
        db.delete(photo)
        db.commit()


def get_all_coor(db):
    data = defaultdict(lambda: {'name': '', 'location': '', 'size': 0, 'coor': {}})
    people = db.query(Person.name, Person.location, Person.lat, Person.lng).filter(not_(or_(Person.lat == None, Person.lng == None))).all()
    for person in people:
        coor_key = f'{person.lat},{person.lng}'
        if data[coor_key]['size'] > 0:
            data[coor_key]['name'] += ', ' + person.name
        else:
            data[coor_key]['name'] = person.name
            data[coor_key]['location'] = person.location
            data[coor_key]['coor'] = {'lat': person.lat, 'lng': person.lng}
        data[coor_key]['size'] += 1
    formatted_data = list(data.values())
    return formatted_data
