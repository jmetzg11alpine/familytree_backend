from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from database import SessionLocal
from helpers import get_all_people, get_person_details, find_potential_relatives, add_new_relative
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
    name_key, coor_key, coor_range = get_all_people(db)
    return {'name_key': name_key, 'coor_key': coor_key, 'coor_range': coor_range}


@router.get('/get_person/{id}')
def get_person(id: int, db: Session = Depends(get_db)):
    retults = get_person_details(db, id)
    return retults


@router.post('/get_potential_relatives')
async def get_potentional_relatives(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    coor = data.get('coor')
    results = find_potential_relatives(db, coor)
    return results


@router.post('/add_relative')
async def add_relative(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    squareCoor = data.get('squareCoor')
    formData = data.get('formData')
    message, name = add_new_relative(formData, squareCoor, db)
    return {'message': message, 'name': name}
