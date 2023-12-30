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
    id = data.get('id')
    return_data = helpers.get_editable_details(id, db)
    return return_data


@router.post('/update_details')
async def update_person_details(request: Request, db: Session = Depends(get_db)):
    data_received = await request.json()
    data = data_received.get('data')
    id = data_received.get('id')
    message, name = helpers.update_details(id, data, db)
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
