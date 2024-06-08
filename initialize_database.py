from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from database import Base
from src.family_tree.models import User
from src.budget.models import AgencyBudget, ForeignAid, FunctionSpending
from urllib.parse import quote_plus
import requests
from collections import defaultdict
import os
import sys
import json
import csv
import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
current_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv()


def start_session_and_create_schemas():
    PASSWORD = os.getenv('DATABASE_PASSWORD')
    DATABASE_URL = os.getenv('DATABASE_URL')

    safe_password = quote_plus(PASSWORD)
    complete_url = DATABASE_URL.replace('<password>', safe_password)
    engine = create_engine(complete_url)

    # creates table
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    return session


def add_users(session):
    user_list = [
        {'username': 'Helen Metzger', 'password': os.getenv('HELEN')},
        {'username': 'Jesse Metzger', 'password': os.getenv('JESSE')},
        {'username': 'Jennifer Metzger', 'password': os.getenv('JENNIFER')},
        {'username': 'Ellina Metzger', 'password': os.getenv('ELLINA')}
    ]

    for user_info in user_list:
        existing_user = session.query(User).filter_by(username=user_info['username']).first()
        if existing_user is None:
            user = User(username=user_info['username'], password=user_info['password'])
            session.add(user)
        else:
            print(f"User {user_info['username']} already exists and was not added")

    session.commit()
    print("Database initialized and users added.")


def fetch_agency_codes():
    base_url = "https://api.usaspending.gov/api/v2/agency/awards/count/"
    agency_codes = {}
    page = 1
    while True:
        response = requests.get(base_url, params={'limit': 100, 'page': page})
        data = response.json()
        results = data['results'][0] if data['results'] else []

        if not results:
            break

        for r in results:
            agency_codes[r['awarding_toptier_agency_name']] = r['awarding_toptier_agency_code']

        page += 1

    return agency_codes


def fetch_budget_resources():
    agency_codes = fetch_agency_codes()

    agency_budgets = {}
    for name, code in agency_codes.items():
        try:
            print(f'budget resource for {name}')
            response = requests.get(f'https://api.usaspending.gov/api/v2/agency/{code}/budgetary_resources/')
            data = response.json()
            # response layout: https://api.usaspending.gov/api/v2/agency/012/budgetary_resources/
            # the index 0 has the most recent year
            budget = data['agency_data_by_year'][0]['agency_budgetary_resources']
            if budget:
                agency_budgets[name] = budget
        except Exception as e:
            print(f'could not find budget resource for {name}, error: {e}')

    return agency_budgets, agency_codes


def fetch_function_spending(agency_codes):
    function_spending = defaultdict(lambda: defaultdict(int))
    for year in range(2017, 2025):
        for agency_name, agency_code in agency_codes.items():
            try:
                print(year, agency_name)
                base_url = f"https://api.usaspending.gov/api/v2/agency/{agency_code}/budget_function/"
                params = {'fiscal_year': year}
                response = requests.get(base_url, params=params)
                results = response.json()['results']

                for result in results:
                    function_name = result['name']
                    amount = result['gross_outlay_amount']
                    function_spending[year][function_name] += amount
            except Exception as e:
                print(f'could not find for budget functions for {agency_name}, {e}')
    return function_spending


def add_agency_budgets(agency_budgets, session):
    for agency, budget in agency_budgets.items():
        agency_budget = AgencyBudget(agency=agency, budget=budget)
        session.add(agency_budget)
    session.commit()
    print('updated agency_budget table')


def add_function_spending(function_spending, session):
    for year, info in function_spending.items():
        for name, amount in info.items():
            function_entry = FunctionSpending(year=year, name=name, amount=amount)
            session.add(function_entry)
    session.commit()
    print('updated function_spending table')


def check_data_quality(agency_budgets, function_spending):
    agency = len(agency_budgets) > 16 and sum([amount for agency, amount in agency_budgets.items()]) > 1192291315.25
    function = len(function_spending) > 5 and sum([item['Net Interest'] for key, item in function_spending.items()]) > 480144186.311
    return agency and function


def clear_previous_data(session):
    session.query(AgencyBudget).delete()
    session.query(FunctionSpending).delete()
    session.commit()
    print('old tables deleted')


def update_date_in_text_file():
    file_name = os.path.join(current_dir, 'src', 'budget', 'data', 'budget_update.txt')
    today = str(datetime.date.today())
    with open(file_name, 'w') as file:
        file.write(today)


def update_budget(session):
    try:
        agency_budgets, agency_codes = fetch_budget_resources()
        function_spending = fetch_function_spending(agency_codes)

        if check_data_quality(agency_budgets, function_spending):
            clear_previous_data(session)

            add_agency_budgets(agency_budgets, session)
            add_function_spending(function_spending, session)
            update_date_in_text_file()

        else:
            print('data quality for budget or function spending did not pass')
    except Exception as e:
        print(f'Could not update Budget tables: {e}')


def prep_foreign_aid_data():
    replacements = {
            'China (Hong Kong, S.A.R., P.R.C.)': 'China',
            'China (P.R.C.)': 'China',
            'China (Tibet)': 'China',
            'Burma (Myanmar)': 'Myanmar',
            'Congo (Brazzaville)': 'Republic of the Congo',
            'Congo (Kinshasa)': 'DR Congo',
            'Korea, Democratic Republic of': 'North Korea',
            'Korea, Republic of': 'South Korea',
            'Sao Tome and Principe': 'São Tomé and Príncipe',
            'Slovak Republic': 'Slovakia',
            'Sudan (former)': 'Sudan',
            'West Bank and Gaza': 'Palestine',
            'Micronesia, Federated States of': 'Micronesia',
            'Kiribati, Republic of': 'Kiribati',
            'Curacao': 'Curaçao',
            'Serbia and Montenegro (former)': 'Serbia'
        }
    exclude = ['World']
    with open('src/budget/data/lat_lng_mapper.json', 'r') as json_file:
        lat_lng_mapper = json.load(json_file)
    data = defaultdict(lambda: defaultdict(float))
    with open('src/budget/data/foreign_aid_all.csv', 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            country = row['Country Name']
            year = row['Fiscal Year']
            amount = row['Constant Dollar Amount']
            country = replacements.get(country, country)
            try:
                if country not in exclude and 'Region' not in country:
                    data[country][year] += int(amount)
            except Exception as e:
                print(country, e)

    entries = []
    for country, years in data.items():
        for year, amount in years.items():
            entries.append({
                'country': country,
                'year': year,
                'amount': amount,
                'lat': lat_lng_mapper[country]['lat'],
                'lng': lat_lng_mapper[country]['lng']
            })
    return entries


def update_foreign_aid(session):
    entries = prep_foreign_aid_data()

    session.query(ForeignAid).delete()

    aids = [
        ForeignAid(
            country=entry['country'],
            year=entry['year'],
            amount=entry['amount'],
            lat=entry['lat'],
            lng=entry['lng'])
        for entry in entries
    ]

    session.bulk_save_objects(aids)
    session.commit()

    print('foreign aid table updated')


if __name__ == '__main__':
    # users aren't saved in the backup. They can be manually added here
    if len(sys.argv) > 1 and sys.argv[1] == 'users':
        session = start_session_and_create_schemas()
        add_users(session)
        session.close()
    elif len(sys.argv) > 1 and sys.argv[1] == 'foreign_aid':
        session = start_session_and_create_schemas()
        update_foreign_aid(session)
        session.close()
    elif len(sys.argv) > 1 and sys.argv[1] == 'budget':
        session = start_session_and_create_schemas()
        update_budget(session)
        session.close()
    else:
        print('add argument: budget, foreign_aid, or users')


# to get the lat and lng of countries.
# works in a jupyter notebook but not in the fastAPI app
# def fetch_country_latlng():
#     url = "https://restcountries.com/v3.1/all"
#     response = requests.get(url)
#     countries = response.json()

#     name_mapper = {
#         'Cape Verde': 'Cabo Verde',
#         'Ivory Coast': "Cote d'Ivoire",
#         'Saint Kitts and Nevis': 'St. Kitts and Nevis',
#         'Saint Lucia': 'St. Lucia',
#         'Saint Vincent and the Grenadines': 'St. Vincent and Grenadines'
#     }

#     lat_lng_mapper = {}
#     for country in countries:
#         name = country['name']['common']
#         if name in name_mapper:
#             name = name_mapper[name]
#         latlng = country['latlng']
#         lat_lng_mapper[country] = {'lat': latlng[0], 'lng': latlng[1]}

#     with open('lat_lng_mapper.json', 'w') as json_file:
#         json.dump(lat_lng_mapper, json_file)
