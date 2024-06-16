from .models import AgencyBudget, ForeignAid, FunctionSpending
from sqlalchemy import and_, func
from collections import defaultdict
from bisect import insort


def get_agency_budget(db):
    budget = db.query(AgencyBudget).order_by(AgencyBudget.budget.desc()).all()

    renaming = {
        "Department of the Treasury": 'Treasury',
        'Department of Health and Human Services': 'Health and Human',
        'Department of Defense': 'Defense',
        'Social Security Administration': 'Social Security',
        'Department of Veterans Affairs': 'Vetrerans Affiars',
        'Department of Agriculture': 'Agriculture',
        'Office of Personnel Management': 'OPM',
        'Department of Housing and Urban Development': 'Housing',
        'Department of Transportation': 'Transportation',
        'Department of Homeland Security': 'Homeland Security',
        'Department of Energy': 'Energy',
        'Department of Commerce': 'Commerce',
        'Department of Education': 'Education',
        'Environmental Protection Agency': 'Environmental',
        'Department of the Interior': 'Interior',
        'Department of State': 'State',
        'General Services Administration': 'General Services',
        'Department of Justice': 'Justice',
        'Department of Labor': 'Labor',
        'Pension Benefit Guaranty Corporation': 'Pension'

    }

    colors = [
        '135, 206, 250',
        '255, 192, 203',
        '221, 160, 221',
        '255, 182, 193',
        '176, 224, 230',
        '173, 216, 230',
        '152, 251, 152',
        '255, 160, 122',
        '250, 128, 114',
        '255, 127, 80',
        '135, 206, 235',
        '147, 112, 219',
        '219, 112, 147'
    ]

    main_data, other_data = [], []
    main_other_value = 0
    other_other_value, other_other_labels = 0, []

    for i, entry in enumerate(budget):
        if i < 9:
            main_data.append({'label': renaming.get(entry.agency, entry.agency),
                              'value': entry.budget,
                              'tooltip': entry.agency,
                              'backgroundColor': 'rgba(' + colors[i] + ', 1)'
                              })
        elif i < 18:
            main_other_value += entry.budget
            other_data.append({'label': renaming.get(entry.agency, entry.agency),
                               'value': entry.budget,
                               'tooltip': entry.agency,
                               'backgroundColor': 'rgba(' + colors[i - 9] + ', 1)'
                               })
        else:
            main_other_value += entry.budget
            other_other_value += entry.budget
            other_other_labels.append((entry.agency, entry.budget))

    other_other_labels.sort(key=lambda x: x[1], reverse=True)
    list_other_other_labels = [(agency, f'${int(budget):,}') for agency, budget in other_other_labels]

    main_data.append({'label': 'other',
                      'value': main_other_value,
                      'tooltip': 'break down in other graph',
                      'backgroundColor': 'rgba(' + colors[9] + ', 0.4)'})

    other_data.append({'label': f'{len(list_other_other_labels)} others',
                       'value': other_other_value,
                       'tooltip': 'break down described below',
                       'backgroundColor': 'rgba(' + colors[9] + ', 0.4)'})

    return main_data, other_data, list_other_other_labels


def normalize_amount(x, _min, _max):
    base_size = 4
    scale_factor = 35
    if x <= _min:
        return base_size
    return base_size + scale_factor * (x - _min) / (_max - _min)


def get_bar_data(data):
    bar_data = {year: 0 for year in range(2015, 2025)}
    for aid in data:
        bar_data[aid.year] += aid.amount
    return [(year, amount) for year, amount in bar_data.items()]


def get_map_data(data, year):
    country_data = {}
    i = 1
    country_set = set()
    for aid in data:
        country = aid.country
        country_set.add(country)
        if country in country_data:
            country_data[country]['amount'] += aid.amount
        else:
            country_data[country] = {'id': i, 'lat': aid.lat, 'lng': aid.lng, 'amount': aid.amount}
            i += 1

    amounts = [info['amount'] for info in country_data.values()]
    _max, _min = max(amounts), min(amounts)

    def make_text(country, info):
        if year == 'all':
            return f"{country} (10 yrs.): ${info['amount']:,.0f}"
        else:
            return f"{country} in {year}: ${info['amount']:,.0f}"

    map_data = []
    for country, info in country_data.items():
        entry = {
            'id': info['id'],
            'lat': info['lat'],
            'lng': info['lng'],
            'text': make_text(country, info),
            'size': normalize_amount(info['amount'], _min, _max)
        }
        map_data.append(entry)

    return map_data, ['all'] + sorted(country_set)


def get_foreign_aid(db, filters):
    country, year = filters['country'], filters['year']

    base_query = db.query(ForeignAid)

    if year != 'all':
        year_query = base_query.filter(ForeignAid.year == year)
    else:
        year_query = base_query

    if country != 'all':
        country_query = base_query.filter(ForeignAid.country == country)
    else:
        country_query = base_query

    map_query = year_query.all()
    bar_query = country_query.all()

    if country != 'all' and year != 'all':
        total_amount = db.query(func.sum(ForeignAid.amount)).filter(and_(ForeignAid.country == country, ForeignAid.year == year)).scalar()
    elif country != 'all':
        total_amount = db.query(func.sum(ForeignAid.amount)).filter(ForeignAid.country == country).scalar()
    elif year != 'all':
        total_amount = db.query(func.sum(ForeignAid.amount)).filter(ForeignAid.year == year).scalar()
    else:
        total_amount = db.query(func.sum(ForeignAid.amount)).scalar()

    map_data, countries = get_map_data(map_query, year)
    bar_data = get_bar_data(bar_query)
    total_amount = total_amount if total_amount is not None else 0

    return map_data, bar_data, total_amount, countries


def get_agency_comparison(db):
    results = db.query(FunctionSpending).all()
    data = defaultdict(list)
    x_labels = set()
    agencies = set()
    keep = {'Transportation': '0, 120, 215',
            'Net Interest': '128, 0, 0',
            'Education, Training, Employment, and Social Services': '255, 165, 0',
            'Energy': '255, 215, 0',
            'Agriculture': '34, 139, 34',
            'National Defense': '80, 80, 80',
            'Health': '0, 191, 255',
            'Commerce and Housing Credit': '105, 105, 105'}

    for entry in results:
        if entry.name in keep:
            value = round(entry.amount / 1000000000)
            insort(data[entry.name], (entry.year, value))
            x_labels.add(entry.year)
            agencies.add((entry.name))

    x_labels = sorted(x_labels)
    return data, x_labels, list(agencies)
