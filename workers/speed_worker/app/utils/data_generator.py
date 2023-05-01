from random import randint

from app.utils.date_manager import is_weekend, get_date_after_days, get_date_from_date_month_year

data = dict()


def generate_waiting_time_for_date(date):
    if is_weekend(date):
        return randint(20, 30)
    else:
        return randint(10, 15)


def generate_waiting_time_data():
    date = get_date_from_date_month_year(1, 1, 2019)
    for i in range(0, 365 * 3):
        data[date] = generate_waiting_time_for_date(date)
        date = get_date_after_days(date, 1)
