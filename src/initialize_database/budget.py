import os
import sys
import requests
from collections import defaultdict
import datetime
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.budget.models import AgencyBudget, FunctionSpending
current_dir = os.path.dirname(os.path.abspath(__file__))


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


def fetch_function_spending(agency_codes):
    functions_to_keep = ['Energy', 'Net Interest', 'Commerce and Housing Credit', 'Transportation', 'Agriculture', 'Health', 'Education, Training, Employment, and Social Services', 'National Defense']
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
                    if function_name in functions_to_keep:
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
    file_name = os.path.join(current_dir, '..', 'budget', 'data', 'budget_update.txt')
    today = str(datetime.date.today())
    with open(file_name, 'w') as file:
        file.write(today)
