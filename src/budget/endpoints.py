from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from src.database import SessionLocal
from . import helpers
router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get('/api/agency_budget')
async def get_agency_budget(db: Session = Depends(get_db)):
    main_data, other_data, list_other_budgets = helpers.get_agency_budget(db)
    return {'main_data': main_data, 'other_data': other_data, 'list_other_budgets': list_other_budgets}


@router.post('/api/foreign_aid')
async def get_foreign_aid(request: Request, db: Session = Depends(get_db)):
    filters = await request.json()
    map_data, bar_data, total_amount, countries = helpers.get_foreign_aid(db, filters)
    return {'map_data': map_data,
            'title_data': {'bar_data': bar_data, 'total_amount': total_amount, 'countries': countries}}


@router.get('/api/agency_comparison')
async def get_agency_comparison(db: Session = Depends(get_db)):
    data, x_labels, agencies = helpers.get_agency_comparison(db)
    return {'line_data': data, 'x_labels': x_labels, 'agencies': agencies}
