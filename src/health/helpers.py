from datetime import datetime, timedelta
from .models import Health
from sqlalchemy import desc, asc, func


def get_max_date(db):
    return db.query(func.max(Health.timestamp)).scalar()


def get_health_data(db, end_date, time_period):
    count = get_day_count(time_period)

    if end_date is None:
        max_timestamp = db.query(func.max(Health.timestamp)).scalar()
        end_date_dt = max_timestamp  + timedelta(days=1)
    else:
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
    query = db.query(Health).filter(Health.timestamp <= end_date_dt).order_by(desc(Health.timestamp))

    if count is not None:
        query = query.limit(count)

    data = query.all()

    for entry in data:
        entry.timestamp = entry.timestamp.strftime('%Y-%m-%d %H:%M')
    return data


def get_chart_data(db, column, end_date, time_period):
    print(end_date)
    count = get_day_count(time_period)
    if end_date is None:
        max_timestamp = db.query(func.max(Health.timestamp)).scalar()
        end_date_dt = max_timestamp + timedelta(days=1)
    else:
        end_date_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
    query = db.query(Health).filter(Health.timestamp <= end_date_dt).order_by(desc(Health.timestamp))

    if count is not None:
        query = query.limit(count)

    data = query.all()

    resp = []
    for entry in data:

        value = getattr(entry, column)
        y = value
        if column == 'pressure':
            y = int(value.split('/')[0])
        resp.append({
            'value': value,
            'y': y,
            'notes': entry.notes,
            'x': entry.timestamp,
            'coffee': entry.coffee,
            'weight': entry.weight,
            'heart_beat': entry.heart_beat,
            'pressure': entry.pressure
        })
    return resp


def get_day_count(time_period):
    if time_period == 'week':
        return 7
    elif time_period == 'month':
        return 30
    else:
        return None


def add_health_entry(db, new_entry):
    try:
        new_entry = Health(
            timestamp=datetime.strptime(new_entry['timestamp'], '%Y-%m-%dT%H:%M'),
            pressure=new_entry['pressure'],
            weight=new_entry['weight'],
            heart_beat=new_entry['heartBeat'],
            coffee=new_entry['coffee'],
            notes=new_entry['notes']
        )
        db.add(new_entry)
        db.commit()
        db.close()
        return True
    except Exception as e:
        print(f'error adding new health entry: {e}')
        return False


def delete_health_entry(db, delete_entry):
    entry = db.query(Health).filter_by(id=delete_entry['id']).first()
    db.delete(entry)
    db.commit()
    return 'entry deleted'
