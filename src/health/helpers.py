from datetime import datetime
from .models import Health
from sqlalchemy import desc, asc


def get_health_data(db, start_date):
    start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    data = db.query(Health).filter(Health.timestamp >= start_date_dt).order_by(desc(Health.timestamp)).all()
    for entry in data:
        entry.timestamp = entry.timestamp.strftime('%Y-%m-%d %H:%M')
    return data


def get_chart_data(db, column, start_date):
    start_date_dt = datetime.strptime(start_date, '%Y-%m-%d')
    data = db.query(Health).filter(Health.timestamp >= start_date_dt).order_by(asc(Health.timestamp)).all()
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
