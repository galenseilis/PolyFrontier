from datetime import datetime, date, timedelta


def get_date_from_string(string):
    return datetime.strptime(string, '%Y-%m-%d')


def get_today_date():
    return date.today()


def get_this_year():
    return date.today().year


def get_date_after_days(date, days):
    return date + timedelta(days=days)


def is_weekend(date):
    return date.weekday() >= 5


def get_day_and_month(date):
    return date.day, date.month


def get_date_from_date_month_year(day, month, year):
    return date(year, month, day)


def get_datetime_from_date_month_year_hour(day, month, year, hour):
    return datetime(year, month, day, hour)
