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


@router.get('/api/get_health_max_date')
async def get_max_date(request: Request, db: Session = Depends(get_db)):
    return helpers.get_max_date(db)


@router.post('/api/get_health')
async def get_health(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    end_date = body.get('endDate')
    time_period = body.get('timePeriod')
    data = helpers.get_health_data(db, end_date, time_period)
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
    body = await request.json()
    column = body['column']
    end_date = body.get('endDate')
    time_period = body.get('timePeriod')
    resp = helpers.get_chart_data(db, column, end_date, time_period)
    return {"data": resp}
