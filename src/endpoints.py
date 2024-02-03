from fastapi import APIRouter, Depends, Request, Header
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import helpers
import os
router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('/')
def read_root():
    return {'message': 'backend is running'}


@router.get('/api/get_people')
def get_people(request: Request, db: Session = Depends(get_db), x_forwarded_for: str = Header(None)):
    name_birth_key, coor_key, coor_range = helpers.get_all_people(db)
    client_ip = x_forwarded_for.split(',')[0] if x_forwarded_for else request.client.host
    helpers.record_visitor(client_ip, db)
    return {'name_birth_key': name_birth_key, 'coor_key': coor_key, 'coor_range': coor_range}


@router.get('/api/get_person/{id}')
def get_person(id: int, db: Session = Depends(get_db)):
    retults = helpers.get_person_details(db, id)
    return retults


@router.post('/api/get_potential_relatives')
async def get_potentional_relatives(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    coor = data.get('coor')
    results = helpers.find_potential_relatives(db, coor, None)
    return results


@router.post('/api/add_relative')
async def add_relative(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    squareCoor = data.get('squareCoor')
    formData = data.get('formData')
    _list = formData['fields']
    for x in _list:
        print(x)
    message, name = helpers.add_new_relative(formData, squareCoor, db)
    if message == 'success':
        current_user = data.get('currentUser')
        helpers.record_action(current_user, 'created', name, db)
    return {'message': message, 'name': name}


@router.post('/api/get_details_to_edit')
async def get_details_to_edit(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    person_id = data.get('id')
    return_data = helpers.get_editable_details(person_id, db)
    return return_data


@router.post('/api/update_details')
async def update_person_details(request: Request, db: Session = Depends(get_db)):
    data_received = await request.json()
    data = data_received.get('data')
    person_id = data_received.get('id')
    message, name = helpers.update_details(person_id, data, db)
    if message == 'success':
        current_user = data_received.get('currentUser')
        recipient_name = helpers.get_name(db, person_id)
        helpers.record_action(current_user, 'edited profile', recipient_name, db)
    return {'message': message, 'name': name}


@router.post('/api/update_bio')
async def update_bio(request: Request, db: Session = Depends(get_db)):
    data_received = await request.json()
    bio = data_received.get('bio')
    name = data_received.get('name')
    file_path = f'./BIOS/{name}.txt'

    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            current_bio = file.read()
    else:
        current_bio = ''

    if bio and bio != current_bio:
        current_user = data_received.get('currentUser')
        helpers.record_action(current_user, 'edited bio', name, db)
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(bio)
    return {'message': 'success'}


@router.post('/api/delete_person')
async def delete_person(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    name = data.get('name')
    helpers.remove_person_and_relations(name, db)
    current_user = data.get('currentUser')
    helpers.record_action(current_user, 'deleted', name, db)
    return {'message': f'{name} was deleted'}


@router.post('/api/photos')
async def get_photos_of_person(request: Request, db: Session = Depends(get_db)):
    data_received = await request.json()
    person_id = data_received.get('id')
    data, paths = helpers.get_photos(person_id, db)
    return {'data': data, 'paths': paths}


@router.post('/api/photo')
async def get_photo_of_person(request: Request, db: Session = Depends(get_db)):
    data_received = await request.json()
    path = data_received.get('path')
    data = helpers.get_photo(path, db)
    return {'data': data}


@router.post('/api/profile_photo')
async def make_profile_photo(request: Request, db: Session = Depends(get_db)):
    data_received = await request.json()
    person_id = data_received.get('person_id')
    person_name = helpers.get_name(db, person_id)
    path = data_received.get('path')
    current_user = data_received.get('currentUser')
    helpers.set_profile_photo(person_id, path, db)
    helpers.record_action(current_user, 'set profile pic', person_name, db)
    return {'message': 'new profile photo set'}


@router.post('/api/update_photo_description')
async def update_photo_description(request: Request, db: Session = Depends(get_db)):
    data_received = await request.json()
    description = data_received.get('description')
    path = data_received.get('path')
    results = helpers.update_description_of_photo(description, path, db)
    if results == 'updated':
        person_name = data_received.get('person_name')
        current_user = data_received.get('currentUser')
        helpers.record_action(current_user, 'photo description updated', person_name, db)
    return {'message': 'description updated'}


@router.post('/api/add_photo')
async def add_photo(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    photo = form_data.get('photo')
    description = form_data.get('description')
    person_id = form_data.get('person_id')
    person_name = helpers.get_name(db, person_id)
    current_user = form_data.get('current_user')
    photo_data = await photo.read()
    helpers.add_new_photo(photo_data, description, person_id, db)
    helpers.record_action(current_user, 'added photo', person_name, db)
    return {'message': 'photo added'}


@router.post('/api/delete_photo')
async def delete_photo(request: Request, db: Session = Depends(get_db)):
    data_received = await request.json()
    path = data_received.get('path')
    person_id = data_received.get('person_id')
    person_name = helpers.get_name(db, person_id)
    current_user = data_received.get('currentUser')
    helpers.delete_one_photo(path, db)
    helpers.record_action(current_user, 'deleted photo', person_name, db)
    return {'message': 'photo deleted'}


@router.get('/api/get_coor')
def get_coor(db: Session = Depends(get_db)):
    data = helpers.get_all_coor(db)
    return data


@router.post('/api/login')
async def login(request: Request, db: Session = Depends(get_db)):
    data_received = await request.json()
    username = data_received.get('username')
    password = data_received.get('password')
    response = helpers.login_user(username, password, db)
    return {'message': response}


@router.get('/api/get_info')
async def get_edits_and_table(db: Session = Depends(get_db)):
    edits, table, url = helpers.get_info(db)
    return {'edits': edits, 'table': table, 'url': url}


@router.post('/api/get_visitors')
async def get_visitors(request: Request, db: Session = Depends(get_db)):
    data_received = await request.json()
    time_range = data_received.get('timeRange')
    visitors = helpers.calculate_visitors(time_range, db)
    return visitors


@router.post('/api/update_location')
async def update_location(request: Request, db: Session = Depends(get_db)):
    data_received = await request.json()
    person_id = data_received.get('personID')
    new_location = data_received.get('newLocation')
    current_user = data_received.get('currentUser')
    message, person_name = helpers.set_new_location(person_id, new_location, db)
    helpers.record_action(current_user, 'moved position', person_name, db)
    return {'message': message}
