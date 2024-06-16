import csv
import sys
import os
from datetime import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.health.models import Health


def update_health(session):
    with open('../health/data.csv', 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            record = Health(
                pressure=row['pressure'],
                weight=float(row['weight']),
                heart_beat=int(row['heart_beat']),
                timestamp=datetime.strptime(row['timestamp'], '%Y-%m-%d %H:%M:%S'),
                coffee=int(row['coffee']),
                notes=row['notes']
            )
            session.add(record)
        session.commit()
        print('health records updated')
