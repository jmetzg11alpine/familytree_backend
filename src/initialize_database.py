from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import Base, User, AgencyBudget, ForeignAid, FunctionSpending
from urllib.parse import quote_plus
import requests
from collections import defaultdict
import os
import sys
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
            budget = data['agency_data_by_year'][0]['agency_budgetary_resources']
            if budget:
                agency_budgets[name] = budget
        except Exception as e:
            print(f'could not find budget resource for {name}, error: {e}')

    return agency_budgets, agency_codes


def fetch_country_latlng():
    url = "https://restcountries.com/v3.1/all"
    response = requests.get(url)
    countries = response.json()

    country_locations = {}
    for country in countries:
        name = country['name']['common']
        latlng = country['latlng']
        country_locations[name] = latlng

    # renaming countries so they match usaspending
    country_locations['Korea, South'] = country_locations['South Korea']
    country_locations['Congo (Kinshasa)'] = country_locations['DR Congo']
    country_locations["Cote D'Ivoire"] = country_locations['Ivory Coast']
    country_locations["Bosnia And Herzegovina"] = country_locations['Bosnia and Herzegovina']
    country_locations["Macedonia"] = country_locations['North Macedonia']
    country_locations["Bahamas, The"] = country_locations['Bahamas']
    country_locations["Czech Republic"] = country_locations['Czechia']
    country_locations["Korea, North"] = country_locations['North Korea']
    country_locations["Congo (Brazzaville)"] = country_locations['Republic of the Congo']

    return country_locations


def fetch_foreign_spending():
    base_url = "https://api.usaspending.gov/api/v2/search/spending_by_geography/"
    payload = {
        'scope': 'place_of_performance',
        'geo_layer': 'country',
        'filters': {
            'time_period': [
                {'start_date': '2024-01-01', 'end_date': '2024-12-31'}
            ]
        }
    }
    response = requests.post(base_url, json=payload)
    results = response.json()['results']

    country_locations = fetch_country_latlng()

    # Palestine = West Bank + Gaza Srip
    foreign_aid = {'Palestine': {'amount': 0, 'latlng': country_locations['Palestine']}}

    for result in results:
        name = result['display_name']
        if name is not None and name in country_locations:
            amount = result['aggregated_amount']
            latlng = country_locations[name]
            foreign_aid[name] = {'amount': amount, 'latlng': latlng}
        elif name == 'West Bank' or name == 'Gaza Strip':
            foreign_aid['Palestine']['amount'] += result['aggregated_amount']
        else:
            print(f'could not find lat lng for {name}')

    return foreign_aid


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
                print(f'could not find for budge functions for {agency_name}, {e}')
    return function_spending


def add_agency_budgets(agency_budgets, session):
    for agency, budget in agency_budgets.items():
        agency_budget = AgencyBudget(agency=agency, budget=budget)
        session.add(agency_budget)
    session.commit()
    print('updated agency_budget table')


def add_foreign_aid(foreign_aid, session):
    for country, info in foreign_aid.items():
        amount = info['amount']
        latlng = info['latlng']
        lat = latlng[0]
        lng = latlng[1]
        country_entry = ForeignAid(country=country, amount=amount, lat=lat, lng=lng)
        session.add(country_entry)
    session.commit()
    print('updated foreign_aid table')


def add_function_spending(function_spending, session):
    for year, info in function_spending.items():
        for name, amount in info.items():
            function_entry = FunctionSpending(year=year, name=name, amount=amount)
            session.add(function_entry)
    session.commit()
    print('updated function_spending table')


def check_data_quality(agency_budgets, foreign_aid, function_spending):
    agency = len(agency_budgets) > 16 and sum([amount for agency, amount in agency_budgets.items()]) > 1192291315.25
    foreign = len(foreign_aid) > 100 and sum([item['amount'] for key, item in foreign_aid.items()]) > 110030453.0696
    function = len(function_spending) > 5 and sum([item['Net Interest'] for key, item in function_spending.items()]) > 480144186.311
    return agency and foreign and function


def clearn_previous_data(session):
    session.query(AgencyBudget).delete()
    session.query(ForeignAid).delete()
    session.query(FunctionSpending).delete()
    session.commit()
    print('old tables deleted')


def update_date_in_text_file():
    file_name = os.path.join(current_dir, 'data', 'budget_update.txt')
    today = str(datetime.date.today())
    with open(file_name, 'w') as file:
        file.write(today)


def update_budget(session):
    try:
        agency_budgets, agency_codes = fetch_budget_resources()
        foreign_aid = fetch_foreign_spending()
        function_spending = fetch_function_spending(agency_codes)

        if check_data_quality(agency_budgets, foreign_aid, function_spending):
            clearn_previous_data(session)

            add_agency_budgets(agency_budgets, session)
            add_foreign_aid(foreign_aid, session)
            add_function_spending(function_spending, session)

            update_date_in_text_file()

        else:
            print('data quality for budget, aid or function spending did not pass')
    except Exception as e:
        print(f'Could not update Budget tables: {e}')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'ALL':
        session = start_session_and_create_schemas()
        add_users(session)
        update_budget(session)
        session.close()
    else:
        session = start_session_and_create_schemas()
        update_budget(session)
        session.close()
