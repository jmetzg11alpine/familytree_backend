from .models import Order, Finance
import pandas as pd
from datetime import datetime, timedelta
import math
from collections import Counter, defaultdict
from .value_variables import warehouse_colors, warehouse_multiplier, sales_colors, customer_colors


def get_start_date(end_date, time_period):
    if time_period == 'week':
        return end_date - timedelta(days=8)
    elif time_period == 'month':
        # extra week is added so first point is aggregated
        return end_date - timedelta(days=7 * 5)
    elif time_period == '6 months':
        # extra month is added so first point is aggregated
        return end_date - timedelta(days=30 * 7)
    elif time_period == 'year':
        # extra month is added
        return end_date - timedelta(days=390)
    else:
        return None


def get_filter_values(db, filters):
    if not filters['filters_retrieved']:
        customer_set = db.query(Finance.customer).distinct().all()
        sales_set = db.query(Finance.sales_person).distinct().all()
        start_location_set = db.query(Order.start_location).distinct().all()
        end_location_set = db.query(Order.end_location).distinct().all()

        customer_set = ['all'] + sorted([x[0] for x in customer_set])
        sales_set = ['all'] + sorted([x[0] for x in sales_set])
        start_location_set = ['all'] + sorted([x[0] for x in start_location_set])
        end_location_set = ['all'] + sorted([x[0] for x in end_location_set])
        return {
            'customers': customer_set,
            'sales': sales_set,
            'start': start_location_set,
            'end': end_location_set
        }
    else:
        return None


def get_time_metrics(df, days, start_date, end_date):
    curr_start = start_date
    curr_end = curr_start + timedelta(days=days)
    unit_count = []
    order_count = []
    margin_list = []
    warehouse = defaultdict(list)
    sales = defaultdict(list)
    bus_seen = set()
    if len(df):
        while curr_end <= end_date:
            temp_df = df[(df['created_at'] >= curr_start) & (df['created_at'] <= curr_end)]

            unit_sum = int(temp_df['units'].sum())
            unit_count.append({'x': curr_end, 'y': unit_sum})

            order_sum = len(temp_df)
            order_count.append({'x': curr_end, 'y': order_sum})

            margin = float(get_margin(temp_df[['driver_cost', 'truck_cost', 'payment_received']]))
            margin_list.append({'x': curr_end, 'y': margin})

            prep_sales(temp_df[['sales_person', 'miles', 'payment_received']], sales, curr_end)
            prep_warehouse(temp_df[['bus_id', 'bus_created_at', 'shipped', 'arrived', 'start_location', 'end_location']], warehouse, bus_seen, start_date, end_date)

            curr_start = curr_end
            curr_end += timedelta(days=days)

    return {
        'unit_count': unit_count,
        'order_count': order_count,
        'margin': margin_list,
        'rpm': get_rpm(sales),
        'warehouse': get_warehouse(warehouse, end_date, days)
    }


def get_margin(temp_df):
    try:
        cost = temp_df['driver_cost'].sum() + temp_df['truck_cost'].sum()
        revenue = temp_df['payment_received'].sum()
        if revenue == 0:
            return 0
        return round(((revenue - cost) / revenue) * 100, 1)
    except Exception as e:
        print(f'Could not calculate margin: {e}')
        return 0


def prep_sales(temp_df, sales, curr_end):
    for sales_name, sales_df in temp_df.groupby('sales_person'):
        rpm = round(sales_df['miles'].sum() / sales_df['payment_received'].sum(), 2)
        sales[sales_name].append({'x': curr_end, 'y': rpm})


def get_rpm(sales):
    datasets = []
    for sales_person in sales:
        data_list = sales[sales_person]
        datasets.append({
            'label': sales_person,
            'data': data_list,
            'borderColor': sales_colors[sales_person]['borderColor'],
            'backgroundColor': sales_colors[sales_person]['backgroundColor'],
            'fill': False,
            'tension': 0.5
        })
    return datasets


def prep_warehouse(temp_df, warehouse, bus_seen, start_date, end_date):
    for _, row in temp_df.iterrows():
        if row['bus_id'] not in bus_seen:
            created_at = row['bus_created_at'].date()
            shipped = None if pd.isna(row['shipped']) else row['shipped'].date()
            arrived = None if pd.isna(row['arrived']) else row['arrived'].date()

            while created_at <= start_date:
                created_at += timedelta(days=1)

            while created_at <= end_date and (shipped is None or created_at <= shipped):
                warehouse[row['start_location']].append(created_at)
                created_at += timedelta(days=1)

            i = 3
            if arrived and i and arrived <= end_date:
                warehouse[row['end_location']].append(arrived)
                arrived += timedelta(days=1)
                i -= 1
            bus_seen.add(row['bus_id'])


def get_warehouse(warehouse, end_date, days):
    data = defaultdict(dict)
    for city in warehouse:
        sorted_values = sorted(warehouse[city])
        cur_date = end_date
        data[city][cur_date] = 0
        while sorted_values:
            date = sorted_values.pop()
            if date <= cur_date - timedelta(days=days):
                while date <= cur_date - timedelta(days=days):
                    cur_date -= timedelta(days=days)
                    data[city][cur_date] = 0
                data[city][cur_date] = 1
            else:
                data[city][cur_date] += 1

    datasets = []
    for city in data:
        data_list = []
        for dt, count in data[city].items():
            value = min(round(count / days * warehouse_multiplier[city]), 100)
            data_list.append({'x': dt, 'y': value})
        data_list = data_list[::-1]
        datasets.append({
            'label': city,
            'data': data_list,
            'borderColor': warehouse_colors[city]['borderColor'],
            'backgroundColor': warehouse_colors[city]['backgroundColor'],
            'fill': True,
            'tension': 0.5
        })
    return datasets


def get_routes(df):
    try:
        route_counts = df.groupby(['start_location', 'end_location']).size().reset_index(name='count')
        routes_sorted = route_counts.sort_values(by='count', ascending=False)
        routes_taken = routes_sorted[routes_sorted['count'] > 0]
        return [(r['start_location'], r['end_location'], r['count']) for i, r in routes_taken.iterrows()]
    except:
        return []


def get_sales_customers(df):
    try:
        customer_counts = df['customer'].value_counts().sort_values(ascending=True)
        customers = customer_counts.index.tolist()

        data = defaultdict(list)
        for sales, sales_df in df.groupby('sales_person'):
            for customer in customers:
                customer_count = len(sales_df[sales_df['customer'] == customer])
                data[sales].append(customer_count)

        datasets = []
        for sales, data in data.items():
            datasets.append({
                'label': sales,
                'data': data,
                'backgroundColor': sales_colors[sales]['backgroundColor'],
                'borderColor': sales_colors[sales]['borderColor'],
                'borderWidth': 1,
                'sum_data': sum(data),
            })

        return {
            'labels': list(customers),
            'datasets': datasets
        }
    except:
        return {'labels': [], 'datasets': []}


def get_proportions(df):
    sales = []
    sales_orders = []
    sales_units = []
    for sales_name, sales_df in df.groupby('sales_person'):
        sales.append(sales_name)
        sales_orders.append(len(sales_df))
        sales_units.append(int(sales_df['units'].sum()))

    customers = []
    customer_orders = []
    customer_units = []
    for customer, customer_df in df.groupby('customer'):
        customers.append(customer)
        customer_orders.append(len(customer_df))
        customer_units.append(int(sales_df['units'].sum()))

    return {
        'sales_orders': {
            'labels': sales,
            'datasets': [{
                'label': 'Sales Orders',
                'data': sales_orders,
                'backgroundColor': [sales_colors[s]['backgroundColor'] for s in sales],
                'borderColor': [sales_colors[s]['borderColor'] for s in sales],
            }]
        },
        'sales_units': {
            'labels': sales,
            'datasets': [{
                'label': 'Sales Units',
                'data': sales_units,
                'backgroundColor': [sales_colors[s]['backgroundColor'] for s in sales],
                'borderColor': [sales_colors[s]['borderColor'] for s in sales],
            }]
        },
        'customer_orders': {
            'labels': customers,
            'datasets': [{
                'label': 'Customer Orders',
                'data': customer_orders,
                'backgroundColor': [customer_colors[c]['backgroundColor'] for c in customers],
                'borderColor': [customer_colors[c]['borderColor'] for c in customers],
            }]
        },
        'customer_units': {
            'labels': customers,
            'datasets': [{
                'label': 'Customer Units',
                'data': customer_units,
                'backgroundColor': [customer_colors[c]['backgroundColor'] for c in customers],
                'borderColor': [customer_colors[c]['borderColor'] for c in customers],
            }]
        }
    }


def get_time(df):
    try:
        names = []
        process = []
        delivery = []
        for sales_person, group_df in df.groupby('sales_person'):
            names.append(sales_person)

            delivery_time = group_df['arrived'] - group_df['created_at']
            delivery_time_minutes = delivery_time.dt.total_seconds() / (60 * 60)
            average_delivery_time = int(delivery_time_minutes.mean())
            delivery.append(average_delivery_time)

            process_time = group_df['shipped'] - group_df['created_at']
            process_time_minues = process_time.dt.total_seconds() / (60 * 60)
            average_process_time = int(process_time_minues.mean())
            process.append(average_process_time)

        return {
            'names': names,
            'process': process,
            'delivery': delivery
        }
    except:
        return {
            'names': [],
            'process': [],
            'delivery': []
        }


def get_table(df):
    try:
        df['created_at_date'] = [x.date() if x else None for x in df['created_at']]
        df['arrived_date'] = [x.date() if x else None for x in df['arrived']]
        df['shipped_date'] = [x.date() if x else None for x in df['shipped']]

        df['order_no'] = df['order_no'].astype(int)
        df['units'] = df['units'].astype(int)
        df['miles'] = df['miles'].astype(int)
        df['payment_received'] = df['payment_received'].astype(int)
        df['truck_cost'] = df['truck_cost'].astype(int)
        df['driver_cost'] = df['driver_cost'].astype(int)
        df['bus_id'] = df['bus_id'].astype(int)
        return df.to_dict(orient='records')
    except:
        return []
