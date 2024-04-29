from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from models import Base, User, AgencyBudget, ForeignAid, FunctionSpending
from urllib.parse import quote_plus
import requests
from collections import defaultdict
import os
import sys
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
                print(f'could not find for budge functions for {agency_name}, {e}')
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


def clearn_previous_data(session):
    session.query(AgencyBudget).delete()
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
        function_spending = fetch_function_spending(agency_codes)

        if check_data_quality(agency_budgets, function_spending):
            clearn_previous_data(session)

            add_agency_budgets(agency_budgets, session)

            update_date_in_text_file()

        else:
            print('data quality for budget or function spending did not pass')
    except Exception as e:
        print(f'Could not update Budget tables: {e}')


def fetch_country_latlng():
    url = "https://restcountries.com/v3.1/all"
    response = requests.get(url)
    countries = response.json()

    name_mapper = {
        'Cape Verde': 'Cabo Verde',
        'Ivory Coast': "Cote d'Ivoire",
        'Saint Kitts and Nevis': 'St. Kitts and Nevis',
        'Saint Lucia': 'St. Lucia',
        'Saint Vincent and the Grenadines': 'St. Vincent and Grenadines'
    }

    lat_dict, lng_dict = {}, {}
    for country in countries:
        name = country['name']['common']
        if name in name_mapper:
            name = name_mapper[name]
        latlng = country['latlng']
        lat_dict[name] = latlng[0]
        lng_dict[name] = latlng[1]

    return lat_dict, lng_dict


def concatenat_foreign_aid_csvs():
    data = defaultdict(lambda: defaultdict(float))
    for year in range(2015, 2025):
        with open(f'data/foreign_aid/foreign_aid_{year}.csv', mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                country = row['Country Name']
                amount = float(row['Constant Dollar Amount'])
                data[country][year] += amount

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

    result = []
    exclude_list = ['Region', 'World', 'United States']
    for country, years in data.items():
        if all(exclude not in country for exclude in exclude_list):
            fixed_country = replacements.get(country, country)
            for year, total_amount in years.items():
                result.append({
                    'country': fixed_country,
                    'year': year,
                    'amount': total_amount
                })
    return result


def update_foreign_aid(session):
    lat_dict, lng_dict = fetch_country_latlng()
    entries = concatenat_foreign_aid_csvs()

    session.query(ForeignAid).delete()

    aids = [
        ForeignAid(
            country=entry['country'],
            year=entry['year'],
            amount=entry['amount'],
            lat=lat_dict[entry['country']],
            lng=lng_dict[entry['country']])
        for entry in entries
    ]

    session.bulk_save_objects(aids)
    session.commit()

    print('foreign aid table updated')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'users':
        session = start_session_and_create_schemas()
        add_users(session)
        session.close()
    elif len(sys.argv) > 1 and sys.argv[1] == 'foreign_aid':
        session = start_session_and_create_schemas()
        update_foreign_aid(session)
        session.close()
    elif len(sys.argv) > 1 and sys.argv[1] == 'users':
        session = start_session_and_create_schemas()
        update_budget(session)
        session.close()
    else:
        print('add argument: budget, foreign_aid, or users')
