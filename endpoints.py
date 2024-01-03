from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from database import SessionLocal
import helpers
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


@router.get('/get_people')
def get_people(db: Session = Depends(get_db)):
    name_key, coor_key, coor_range = helpers.get_all_people(db)
    return {'name_key': name_key, 'coor_key': coor_key, 'coor_range': coor_range}


@router.get('/get_person/{id}')
def get_person(id: int, db: Session = Depends(get_db)):
    retults = helpers.get_person_details(db, id)
    return retults


@router.post('/get_potential_relatives')
async def get_potentional_relatives(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    coor = data.get('coor')
    results = helpers.find_potential_relatives(db, coor, None)
    return results


@router.post('/add_relative')
async def add_relative(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    squareCoor = data.get('squareCoor')
    formData = data.get('formData')
    message, name = helpers.add_new_relative(formData, squareCoor, db)
    return {'message': message, 'name': name}


@router.post('/get_details_to_edit')
async def get_details_to_edit(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    person_id = data.get('id')
    return_data = helpers.get_editable_details(person_id, db)
    return return_data


@router.post('/update_details')
async def update_person_details(request: Request, db: Session = Depends(get_db)):
    data_received = await request.json()
    data = data_received.get('data')
    person_id = data_received.get('id')
    message, name = helpers.update_details(person_id, data, db)
    return {'message': message, 'name': name}


@router.post('/update_bio')
async def update_bio(request: Request):
    data_received = await request.json()
    bio = data_received.get('bio')
    name = data_received.get('name')
    file_path = f'./BIOS/{name}.txt'
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(bio)
    return {'message': 'success'}


@router.post('/delete_person')
async def delete_person(request: Request, db: Session = Depends(get_db)):
    data_received = await request.json()
    name = data_received.get('name')
    helpers.remove_person_and_relations(name, db)
    return {'message': f'{name} was deleted'}


@router.post('/photos')
async def get_photos_of_person(request: Request, db: Session = Depends(get_db)):
    data_recieved = await request.json()
    person_id = data_recieved.get('id')
    data, paths = helpers.get_photos(person_id, db)
    return {'data': data, 'paths': paths}


@router.post('/photo')
async def get_photo_of_person(request: Request, db: Session = Depends(get_db)):
    data_recieved = await request.json()
    path = data_recieved.get('path')
    data = helpers.get_photo(path, db)
    return {'data': data}


@router.post('/profile_photo')
async def make_profile_photo(request: Request, db: Session = Depends(get_db)):
    data_recieved = await request.json()
    person_id = data_recieved.get('person_id')
    path = data_recieved.get('path')
    helpers.set_profile_photo(person_id, path, db)
    return {'message': 'new profile photo set'}


@router.post('/update_photo_description')
async def update_photo_description(request: Request, db: Session = Depends(get_db)):
    data_recieved = await request.json()
    description = data_recieved.get('description')
    path = data_recieved.get('path')
    helpers.update_description_of_photo(description, path, db)
    return {'message': 'description updated'}


@router.post('/add_photo')
async def add_photo(request: Request, db: Session = Depends(get_db)):
    form_data = await request.form()
    photo = form_data.get('photo')
    description = form_data.get('description')
    person_id = form_data.get('person_id')
    photo_data = await photo.read()
    helpers.add_new_photo(photo_data, description, person_id, db)
    return {'message': 'photo added'}


@router.post('/delete_photo')
async def delete_photo(request: Request, db: Session = Depends(get_db)):
    data_recieved = await request.json()
    path = data_recieved.get('path')
    helpers.delete_one_photo(path, db)
    return {'message': 'photo deleted'}


@router.get('/get_coor')
def get_coor(db: Session = Depends(get_db)):
    data = helpers.get_all_coor(db)
    return data
