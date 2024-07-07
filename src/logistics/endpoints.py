from fastapi import APIRouter, Depends, Request
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import asc, func
from database import SessionLocal
import pandas as pd
from .models import Order, Bus, Finance
from . import helpers
from .value_variables import period_days
router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post('/api/logistics_get_data')
async def get_count_revenue(request: Request, db: Session = Depends(get_db)):
    filters = await request.json()
    time_period = filters['time_period']
    days = period_days[time_period]
    end_date = datetime.strptime(filters['end_date'], '%Y-%m-%d')
    start_date = helpers.get_start_date(end_date, time_period)

    query = db.query(
        Order.order_no,
        Order.start_location,
        Order.end_location,
        Order.miles,
        Order.units,
        Order.created_at,
        Order.split,
        Finance.driver_cost,
        Finance.truck_cost,
        Finance.payment_received,
        Finance.sales_person,
        Finance.customer,
        Bus.id.label('bus_id'),
        Bus.created_at.label('bus_created_at'),
        Bus.shipped,
        Bus.arrived
    ).join(Order.finance).join(Order.bus).filter(
        Order.created_at <= end_date
    )

    if start_date:
        query = query.filter(Order.created_at >= start_date)
    else:
        start_date = db.query(func.min(Order.created_at)).scalar()

    if filters['customer'] != 'all':
        query = query.filter(Finance.customer == filters['customer'])
    if filters['sales'] != 'all':
        query = query.filter(Finance.sales_person == filters['sales'])
    if filters['start_location'] != 'all':
        query = query.filter(Order.start_location == filters['start_location'])
    if filters['end_location'] != 'all':
        query = query.filter(Order.end_location == filters['end_location'])

    results = query.order_by(asc(Order.created_at)).all()
    results_list = [result._asdict() for result in results]
    df = pd.DataFrame(results_list)
    if len(df):
        routes = helpers.get_routes(df[['start_location', 'end_location']])
        sales_customer = helpers.get_sales_customers(df[['customer', 'sales_person']])
        proportions = helpers.get_proportions(df[['sales_person', 'customer', 'units']])
        time = helpers.get_time(df[['created_at', 'sales_person', 'shipped', 'arrived']])
        table = helpers.get_table(df)
        df['created_at'] = [x.date() for x in df['created_at']]

    time_metrics = helpers.get_time_metrics(df, days, start_date.date(), end_date.date())

    return {
        'data': {
            'unit_count': time_metrics['unit_count'],
            'order_count': time_metrics['order_count'],
            'margin': time_metrics['margin'],
            'rpm': time_metrics['rpm'],
            'warehouse_capacity': time_metrics['warehouse'],
            'routes': routes,
            'sales_customers': sales_customer,
            'proportions': proportions,
            'time': time,
            'table': table
        },
        'filters': helpers.get_filter_values(db, filters)
    }
