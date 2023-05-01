from datetime import datetime, date, timedelta

import pandas as pd

LOCALIZATION = 'UTC'
TZ_ZONE = 'Europe/Paris'


def get_local_date_time_from_string_with_timezone(string):
    return datetime.strptime(string[:18], '%Y-%m-%d %H:%M:%S') + timedelta(hours=int(string[21]))

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

def is_rush_hour(date):
    return 7 < date.hour < 9 | 17 < date.hour < 20


def get_day_and_month(date):
    return date.day, date.month


def get_date_from_date_month_year(day, month, year):
    return date(year, month, day)


def __from_timestamp(df, column):
    try:
        df[column] = pd.to_datetime(df[column], unit="s").dt.tz_localize(LOCALIZATION).dt.tz_convert(TZ_ZONE)
    except Exception:
        pass


def __from_datetime(df, column):
    try:
        df[column] = pd.to_datetime(df[column]).dt.tz_localize(LOCALIZATION).dt.tz_convert(TZ_ZONE)
    except Exception:
        pass


def __from_localized_datetime(df, column):
    try:
        df[column] = pd.to_datetime(df[column]).dt.tz_convert(TZ_ZONE)
    except Exception:
        pass


def __from_localized_utc_datetime(df, column):
    df[column] = pd.to_datetime(df[column], utc=True).dt.tz_convert(TZ_ZONE)


def convert_column_to_datetime(df, column):
    __from_timestamp(df, column) or __from_datetime(df, column) or __from_localized_datetime(df, column) or \
    __from_localized_utc_datetime(df, column)


def parse_influx_datetime(df, column):
    df[column] = pd.to_datetime(df[column], format='%Y-%m-%dT%H:%M:%SZ').dt.tz_localize(LOCALIZATION) \
        .dt.tz_convert(TZ_ZONE)
