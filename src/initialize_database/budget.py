import os
import sys
import csv
import requests
from collections import defaultdict
import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.budget.models import AgencyBudget, FunctionSpending
current_dir = os.path.dirname(os.path.abspath(__file__))


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

    file_name = os.path.join(current_dir, '..', 'budget', 'data', 'agency_codes.csv')
    with open(file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Agency Name', 'Agency Code'])
        for agency_name, agency_code in agency_codes.items():
            writer.writerow([agency_name, agency_code])


def fetch_budget_resources():
    agency_codes = {}
    agency_file_name = os.path.join(current_dir, '..', 'budget', 'data', 'agency_codes.csv')
    with open(agency_file_name, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            agency_codes[row['Agency Name']] = row['Agency Code']

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

    budget_file_name = os.path.join(current_dir, '..', 'budget', 'data', 'agency_resources.csv')
    with open(budget_file_name, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Agency', 'Budget'])
        for agency, budget in agency_budgets.items():
            writer.writerow([agency, budget])


def fetch_function_spending(years_to_check):
    functions_to_keep = ['Energy', 'Net Interest', 'Commerce and Housing Credit', 'Transportation', 'Agriculture', 'Health', 'Education, Training, Employment, and Social Services', 'National Defense']

    agency_codes = {}
    agency_file_name = os.path.join(current_dir, '..', 'budget', 'data', 'agency_codes.csv')
    with open(agency_file_name, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            agency_codes[row['Agency Name']] = row['Agency Code']

    for year in years_to_check:
        function_spending = defaultdict(int)
        for agency_name, agency_code in agency_codes.items():
            try:
                print(year, agency_name)
                base_url = f"https://api.usaspending.gov/api/v2/agency/{agency_code}/budget_function/"
                params = {'fiscal_year': year}
                response = requests.get(base_url, params=params)
                results = response.json()['results']

                for result in results:
                    function_name = result['name']
                    if function_name in functions_to_keep:
                        amount = result['gross_outlay_amount']
                        function_spending[function_name] += amount
            except Exception as e:
                print(f'could not find for budget functions for {agency_name}, {e}')
        function_file_name = os.path.join(current_dir, '..', 'budget', 'data', f'functions_{year}.csv')
        with open(function_file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Function', 'Amount'])
            for function, amount in function_spending.items():
                writer.writerow([function, amount])


def add_agency_budgets(session):
    agency_budgets = {}
    agency_file_name = os.path.join(current_dir, '..', 'budget', 'data', 'agency_resources.csv')
    with open(agency_file_name, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            agency_budget = AgencyBudget(agency=row['Agency'], budget=row['Budget'])
            session.add(agency_budget)
    session.commit()
    print('agency budget table updated')


def add_function_spending(session):
    for year in range(2017, 2025):
        function_file_name = os.path.join(current_dir, '..', 'budget', 'data', f'functions_{year}.csv')
        with open(function_file_name, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                function_entry = FunctionSpending(year=year, name=row['Function'], amount=row['Amount'])
                session.add(function_entry)
    session.commit()
    print('function spending table updated')


def update_date_in_text_file():
    file_name = os.path.join(current_dir, '..', 'budget', 'data', 'budget_update.txt')
    today = str(datetime.date.today())
    with open(file_name, 'w') as file:
        file.write(today)


def update_budget(session):
    # updates the csv files

    # all the unique agency codes for the government
    # fetch_agency_codes()

    # budget resources for the most recent year
    # fetch_budget_resources()

    # get historical function spending (2017, 2025)
    # years_to_check = [2024]
    # fetch_function_spending(years_to_check)

    add_agency_budgets(session)
    add_function_spending(session)
    update_date_in_text_file()
