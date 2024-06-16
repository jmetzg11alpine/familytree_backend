from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from database import SessionLocal
from . import helpers
router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post('/api/get_health')
async def get_health(request: Request, db: Session = Depends(get_db)):
    start_date = await request.json()
    data = helpers.get_health_data(db, start_date)
    return {'data': data}


@router.post('/api/add_health_entry')
async def add_health_entry(request: Request, db: Session = Depends(get_db)):
    new_entry = await request.json()
    response = helpers.add_health_entry(db, new_entry)
    if response:
        return {'msg': 'entry added', 'status': 'Success'}
    return {'msg': 'could not add entry', 'status': 'Failure'}


@router.post('/api/delete_health_entry')
async def delete_health_entry(request: Request, db: Session = Depends(get_db)):
    delete_entry = await request.json()
    rsp = helpers.delete_health_entry(db, delete_entry)
    return {'msg': rsp}


@router.post('/api/get_health_chart_data')
async def get_chart_data(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    column = data['column']
    start_date = data['startDate']
    resp = helpers.get_chart_data(db, column, start_date)
    return {"data": resp}
