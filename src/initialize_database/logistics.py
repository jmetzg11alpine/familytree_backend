from src.logistics.models import Order, Bus, Finance
from datetime import datetime, timedelta
import random
import csv
import math


class OrderInstance:
    def __init__(self, order_no, start_location, end_location, miles, units, created_at, due_date, split, bus_id, finance_id):
        self.order_no = order_no
        self.start_location = start_location
        self.end_location = end_location
        self.miles = miles
        self.units = units
        self.created_at = created_at
        self.due_date = due_date
        self.split = split
        self.bus_id = bus_id
        self.finance_id = finance_id

    def split_order(self, left_over_units):
        new_order = OrderInstance(
            order_no=self.order_no,
            start_location=self.start_location,
            end_location=self.end_location,
            miles=self.miles,
            units=left_over_units,
            created_at=self.created_at,
            split=True,
            due_date=self.due_date,
            bus_id=None,
            finance_id=self.finance_id
        )
        self.units -= left_over_units
        self.split = True
        return new_order

    def to_dict(self):
        return self.__dict__


class BusInstance:
    def __init__(self, id, units, created_at, shipped=None, arrived=None):
        self.id = id
        self.units = units
        self.created_at = created_at
        self.shipped = shipped
        self.arrived = arrived

    def add_arrived_date(self, order):
        miles = order.miles
        avg_mph = 50
        multiplier = random.uniform(0.7, 1.2)
        effective_speed = avg_mph * multiplier
        travel_time_hours = miles / effective_speed
        self.arrived = self.shipped + timedelta(hours=travel_time_hours)

    def to_dict(self):
        return self.__dict__


class FinanceInstance:
    def __init__(self, id, driver_cost, truck_cost, payment_received, sales_person, customer):
        self.id = id
        self.driver_cost = driver_cost
        self.truck_cost = truck_cost
        self.payment_received = payment_received
        self.sales_person = sales_person
        self.customer = customer

    def to_dict(self):
        return self.__dict__


class DataManager:
    warehouses = ['San Diego', 'Phoenix', 'Dallas', 'Las Vegas', 'Denver']
    warehouses_weights = [.4, .1, .15, .05, .3]
    distances = {
        ('San Diego', 'Phoenix'): 367,
        ('San Diego', 'Dallas'): 1360,
        ('San Diego', 'Las Vegas'): 338,
        ('San Diego', 'Denver'): 1090,
        ('Phoenix', 'Dallas'): 1065,
        ('Phoenix', 'Las Vegas'): 203,
        ('Phoenix', 'Denver'): 865,
        ('Dallas', 'Las Vegas'): 1222,
        ('Dallas', 'Denver'): 793,
        ('Las Vegas', 'Denver'): 748
    }
    route_payment_multipliers = {
        ('San Diego', 'Las Vegas'): 1.6,
        ('San Diego', 'Phoenix'): 1.5,
        ('San Diego', 'Dallas'): 1.4,
        ('San Diego', 'Denver'): 1.3,
        ('Phoenix', 'Dallas'): 1.2,
        ('Phoenix', 'Las Vegas'): 1.1,
        ('Phoenix', 'Denver'): 1.25,
        ('Dallas', 'Las Vegas'): 1.15,
        ('Dallas', 'Denver'): 1.2,
        ('Las Vegas', 'Denver'): 1.3,
    }

    sales_person_weights = {
        ('San Diego', 'Las Vegas'): {'Bill': .3, 'John': .0, 'Sue': .25, 'Frank': .45, 'Mary': .0},
        ('San Diego', 'Phoenix'): {'Bill': .0, 'John': .2, 'Sue': .4, 'Frank': .0, 'Mary': .4},
        ('San Diego', 'Dallas'): {'Bill': .2, 'John': .15, 'Sue': .0, 'Frank': .0, 'Mary': .65},
        ('San Diego', 'Denver'): {'Bill': .3, 'John': .1, 'Sue': .6, 'Frank': 0, 'Mary': 0},
        ('Phoenix', 'Dallas'): {'Bill': 0, 'John': 0, 'Sue': .55, 'Frank': .35, 'Mary': .1},
        ('Phoenix', 'Las Vegas'): {'Bill': 0, 'John': .3, 'Sue': .2, 'Frank': .35, 'Mary': .15},
        ('Phoenix', 'Denver'): {'Bill': 0, 'John': .3, 'Sue': .3, 'Frank': .4, 'Mary': 0},
        ('Dallas', 'Las Vegas'): {'Bill': 0, 'John': .55, 'Sue': 0, 'Frank': .45, 'Mary': .1},
        ('Dallas', 'Denver'): {'Bill': .1, 'John': .35, 'Sue': 0, 'Frank': .55, 'Mary': .1},
        ('Las Vegas', 'Denver'): {'Bill': 0, 'John': 0, 'Sue': .4, 'Frank': .5, 'Mary': .1},
    }

    sales_person_cost_multipliers = {
        'Sue': 1.09,
        'Mary': 1.14,
        'John': 1.12,
        'Frank': 1.11,
        'Bill': 1.08
    }
    customer_weights = {
        ('San Diego', 'Las Vegas'): {
            'Publix': .3,
            'Target': .3,
            'Walmart': 0,
            'Kroger': 0,
            'Dollar Tree': 0,
            'Ace Hardware': 0,
            'Best Buy': .1,
            'Albertsons': .1,
            'Rite Aid': .1,
            'Dollar General': .1
        },
        ('San Diego', 'Phoenix'): {
            'Publix': 0,
            'Target': .3,
            'Walmart': .3,
            'Kroger': 0,
            'Dollar Tree': 0,
            'Ace Hardware': 0,
            'Best Buy': .1,
            'Albertsons': .1,
            'Rite Aid': .1,
            'Dollar General': .1
        },
        ('San Diego', 'Dallas'): {
            'Publix': 0,
            'Target': 0,
            'Walmart': .3,
            'Kroger': .3,
            'Dollar Tree': 0,
            'Ace Hardware': 0,
            'Best Buy': .1,
            'Albertsons': .1,
            'Rite Aid': .1,
            'Dollar General': .1
        },
        ('San Diego', 'Denver'): {
            'Publix': 0,
            'Target': 0,
            'Walmart': 0,
            'Kroger': .3,
            'Dollar Tree': .3,
            'Ace Hardware': 0,
            'Best Buy': .1,
            'Albertsons': .1,
            'Rite Aid': .1,
            'Dollar General': .1
        },
        ('Phoenix', 'Dallas'): {
            'Publix': 0,
            'Target': 0,
            'Walmart': 0,
            'Kroger': 0,
            'Dollar Tree': .3,
            'Ace Hardware': .3,
            'Best Buy': .1,
            'Albertsons': .1,
            'Rite Aid': .1,
            'Dollar General': .1
        },
        ('Phoenix', 'Las Vegas'): {
            'Publix': .1,
            'Target': 0,
            'Walmart': 0,
            'Kroger': 0,
            'Dollar Tree': 0,
            'Ace Hardware': .3,
            'Best Buy': .3,
            'Albertsons': .1,
            'Rite Aid': .1,
            'Dollar General': .1
        },
        ('Phoenix', 'Denver'): {
            'Publix': .1,
            'Target': .1,
            'Walmart': 0,
            'Kroger': 0,
            'Dollar Tree': 0,
            'Ace Hardware': 0,
            'Best Buy': .3,
            'Albertsons': .3,
            'Rite Aid': .1,
            'Dollar General': .1
        },
        ('Dallas', 'Las Vegas'): {
            'Publix': .1,
            'Target': .1,
            'Walmart': .1,
            'Kroger': 0,
            'Dollar Tree': 0,
            'Ace Hardware': 0,
            'Best Buy': 0,
            'Albertsons': 3,
            'Rite Aid': 3,
            'Dollar General': .1
        },
        ('Dallas', 'Denver'): {
            'Publix': .1,
            'Target': .1,
            'Walmart': .1,
            'Kroger': .1,
            'Dollar Tree': 0,
            'Ace Hardware': 0,
            'Best Buy': 0,
            'Albertsons': 0,
            'Rite Aid': .3,
            'Dollar General': .3
        },
        ('Las Vegas', 'Denver'): {
            'Publix': .5,
            'Target': 0,
            'Walmart': 0,
            'Kroger': 0,
            'Dollar Tree': 0,
            'Ace Hardware': 0,
            'Best Buy': 0,
            'Albertsons': 0,
            'Rite Aid': 0,
            'Dollar General': .5
        },
    }
    customer_payment_multipliers = {
        'Publix': 1.58,
        'Target': 1.44,
        'Walmart': 1.38,
        'Kroger': 1.24,
        'Dollar Tree': 1.16,
        'Ace Hardware': 1.59,
        'Best Buy': 1.45,
        'Albertsons': 1.38,
        'Rite Aid': 1.25,
        'Dollar General': 1.18
    }

    def __init__(self):
        self.bus_id = 0
        self.order_no = 1
        self.finance_id = 0
        self.buses = {}
        self.current_date = datetime.now() - timedelta(days=(365 * 2))
        self.cost_seasonal_multiplier = None
        self.payment_seasonal_multiplier = None

        self.order_file = open('../logistics/data/orders.csv', 'w', newline='')
        self.bus_file = open('../logistics/data/buses.csv', 'w', newline='')
        self.finance_file = open('../logistics/data/finance.csv', 'w', newline='')

        self.order_writer = csv.DictWriter(self.order_file, fieldnames=[
            'order_no', 'start_location', 'end_location', 'miles', 'units', 'created_at', 'due_date', 'split', 'bus_id', 'finance_id'])
        self.bus_writer = csv.DictWriter(self.bus_file, fieldnames=[
            'id', 'units', 'created_at', 'shipped', 'arrived'])
        self.finance_writer = csv.DictWriter(self.finance_file, fieldnames=[
            'id', 'driver_cost', 'truck_cost', 'payment_received', 'sales_person', 'customer'])

        self.order_writer.writeheader()
        self.bus_writer.writeheader()
        self.finance_writer.writeheader()

    def make_starting_variables(self):
        start_date = self.current_date
        end_date = datetime.now() + timedelta(days=365 // 2)
        total_days = (end_date - start_date).days
        return total_days

    def make_seasonal_multipliers(self):
        # mid winter: cost = 1.1, payment = 1.4
        # mid summer: cost = 0.8, payment = 1.1
        day_of_year = self.current_date.timetuple().tm_yday
        self.cost_seasonal_multiplier = 1.05 + (1.05 - 1.15) * math.sin((day_of_year / 365) * 2 * math.pi)
        self.payment_seasonal_multiplier = 1.2 + (1.1 - 1.2) * math.sin((day_of_year / 365) * 2 * math.pi)

    @classmethod
    def get_miles(cls, a, b):
        return cls.distances.get((a, b)) or cls.distances.get((b, a)) or 0

    @staticmethod
    def check_location(a, b):
        if a == b:
            if a == 'San Diego':
                return a, 'Las Vegas'
            else:
                return a, 'San Diego'
        return a, b

    def make_an_order(self):
        start_location = random.choices(self.warehouses, weights=self.warehouses_weights, k=1)[0]
        end_location = random.choices(self.warehouses, weights=self.warehouses_weights, k=1)[0]
        start_location, end_location = self.check_location(start_location, end_location)

        def generate_units(mean=50, std=20, min_value=5):
            while True:
                units = int(random.normalvariate(mean, std))
                if units >= min_value:
                    return units

        return OrderInstance(
            order_no=str(self.order_no),
            start_location=start_location,
            end_location=end_location,
            miles=self.get_miles(start_location, end_location),
            units=generate_units(),
            created_at=self.current_date,
            due_date=self.current_date + timedelta(days=random.randrange(4, 16)),
            split=False,
            bus_id=None,
            finance_id=None
        )

    def add_finance_data(self, order):
        self.finance_id += 1
        order.finance_id = self.finance_id

        route = (order.start_location, order.end_location)
        reverse_route = (order.end_location, order.start_location)
        route_payment_multiplier = self.route_payment_multipliers.get(route, self.route_payment_multipliers.get(reverse_route))

        sales_person_weights = self.sales_person_weights.get(
            route,
            self.sales_person_weights.get(reverse_route)
        )
        sales_person = random.choices(
            list(sales_person_weights.keys()),
            weights=list(sales_person_weights.values()), k=1)[0]
        sales_person_cost_multiplier = self.sales_person_cost_multipliers.get(sales_person)

        customer_weights = self.customer_weights.get(
            route,
            self.customer_weights.get(reverse_route)
        )
        customer = random.choices(
            list(customer_weights.keys()),
            weights=list(customer_weights.values()), k=1)[0]
        customer_payment_multiplier = self.customer_payment_multipliers.get(customer)

        driver_cost = order.miles * random.uniform(.7, 1.05) * self.cost_seasonal_multiplier * sales_person_cost_multiplier

        truck_cost = order.miles * random.uniform(.7, 1.05) * self.cost_seasonal_multiplier * sales_person_cost_multiplier

        payment_received = order.miles * random.uniform(.95, 1.08) * self.payment_seasonal_multiplier * route_payment_multiplier * customer_payment_multiplier

        finance_instance = FinanceInstance(
            id=self.finance_id,
            driver_cost=driver_cost,
            truck_cost=truck_cost,
            payment_received=payment_received,
            sales_person=sales_person,
            customer=customer
        )
        self.finance_writer.writerow(finance_instance.to_dict())

    def add_to_bus(self, order):
        route = order.start_location + '-' + order.end_location
        bus = None
        new_order = None

        if route in self.buses:
            order.bus_id = self.buses[route].id
            if self.buses[route].units + order.units <= 100:
                self.buses[route].units += order.units
                if self.buses[route].units == 100:
                    bus = self.buses[route]
                    bus.shipped = self.current_date
                    del self.buses[route]
                    self.bus_id += 1
                    self.buses[route] = self.make_new_bus()
            else:
                available_units = 100 - self.buses[route].units
                self.buses[route].units = 100
                bus = self.buses[route]
                bus.shipped = self.current_date
                del self.buses[route]
                left_over_units = order.units - available_units
                if left_over_units > 0:
                    new_order = order.split_order(left_over_units)
                    self.bus_id += 1
                    self.buses[route] = self.make_new_bus()

        else:
            self.bus_id += 1
            order.bus_id = self.bus_id
            self.buses[route] = self.make_new_bus()

        return bus, order, new_order

    def make_new_bus(self):
        return BusInstance(
            id=self.bus_id,
            units=0,
            created_at=self.current_date
        )

    def complete_bus(self, route, order):
        order_units = order.units
        available_units = 100 - self.buses[route].units
        left_over_units = (available_units - order_units) * -1
        self.buses[route].units = 100
        bus = self.buses[route]
        bus.shipped = self.current_date
        del self.buses[route]
        self.bus_id += 1
        self.buses[route] = self.make_new_bus()
        self.buses[route].units = left_over_units
        return bus, left_over_units

    def record_data(self, bus, order):
        if bus:
            try:
                bus.add_arrived_date(order)
                self.bus_writer.writerow(bus.to_dict())
            except Exception as e:
                print(e)
                print(bus.to_dict())
        try:
            self.order_writer.writerow(order.to_dict())
        except Exception as e:
            print(e)
            print(order.to_dict())

    def add_remaing_buses(self):
        for key, bus_instance in self.buses.items():
            self.bus_writer.writerow(bus_instance.to_dict())

    def close_files(self):
        self.order_file.close()
        self.bus_file.close()
        self.finance_file.close()


def process_order(order_details, data_manager):
    while True:
        bus, order, new_order = data_manager.add_to_bus(order_details)
        data_manager.record_data(bus, order)

        if not new_order:
            break

        order_details = new_order


def seasonal_factor(day_of_year):
    return 12 + 8 * math.sin((day_of_year / 365.0) * 2 * math.pi)


def make_data():
    data_manager = DataManager()
    total_days = data_manager.make_starting_variables()
    start_date = data_manager.current_date

    for day in range(total_days):
        current_date = start_date + timedelta(days=day)
        day_of_year = current_date.timetuple().tm_yday
        max_orders = int(seasonal_factor(day_of_year))
        data_manager.make_seasonal_multipliers()

        for _ in range(random.randrange(max_orders)):
            order_details = data_manager.make_an_order()
            data_manager.add_finance_data(order_details)
            process_order(order_details, data_manager)
            data_manager.order_no += 1

        data_manager.current_date += timedelta(days=1)

    data_manager.add_remaing_buses()
    data_manager.close_files()
    print('csv files from orders, buses and finance made')


def add_data(session):

    def cut_secs(dt):
        return dt.replace(microsecond=0)

    def parse_datetime(value, dt_format='%Y-%m-%d %H:%M:%S.%f'):
        return cut_secs(datetime.strptime(value, dt_format)) if value else None

    with open('../logistics/data/buses.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            bus = Bus(
                id=int(row['id']),
                units=int(row['units']),
                created_at=parse_datetime(row['created_at']),
                shipped=parse_datetime(row['shipped']),
                arrived=parse_datetime(row['arrived'])
            )
            session.add(bus)
        session.commit()

    with open('../logistics/data/finance.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            finance = Finance(
                id=int(row['id']),
                driver_cost=round(float(row['driver_cost'])),
                truck_cost=round(float(row['truck_cost'])),
                payment_received=round(float(row['payment_received'])),
                sales_person=row['sales_person'],
                customer=row['customer']
            )
            session.add(finance)
        session.commit()

    with open('../logistics/data/orders.csv', 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            order = Order(
                order_no=row['order_no'],
                start_location=row['start_location'],
                end_location=row['end_location'],
                miles=int(row['miles']),
                units=int(row['units']),
                created_at=parse_datetime(row['created_at'], '%Y-%m-%d %H:%M:%S.%f'),
                due_date=parse_datetime(row['due_date'], '%Y-%m-%d %H:%M:%S.%f'),
                split=row['split'] == 'True',
                bus_id=int(row['bus_id']),
                finance_id=int(row['finance_id'])
            )
            session.add(order)
        session.commit()

    print('finance, bus and order data entered into mySQL database')


def update_logistics(session):
    make_data()
    add_data(session)
