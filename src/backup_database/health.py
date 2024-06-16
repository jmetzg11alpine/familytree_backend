import csv
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.health.models import Health
from database import SessionLocal


def save_health_data():
    session = SessionLocal()
    all_data = session.query(Health).all()

    with open('../health/data.csv', mode='w', newline='') as file:
        writer = csv.writer(file)

        writer.writerow(['id', 'pressure', 'weight', 'heart_beat', 'timestamp', 'coffee', 'notes'])

        for data in all_data:
            writer.writerow([
                data.id,
                data.pressure,
                data.weight,
                data.heart_beat,
                data.timestamp,
                data.coffee,
                data.notes
            ])

    session.close()
    print('health data saved')
