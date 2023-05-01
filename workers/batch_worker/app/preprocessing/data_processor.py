import pandas as pd

from app.date_manager import convert_column_to_datetime, get_date_without_hour_from_timestamp, \
    get_date_hour_without_minute_from_timestamp


def join_daily_data(weather_data : pd.DataFrame, traffic_data : pd.DataFrame) -> pd.DataFrame:
    """
    Joins weather and traffic data.
    """
    convert_column_to_datetime(weather_data, "ts")
    convert_column_to_datetime(traffic_data, "ts")
    get_date_without_hour_from_timestamp(weather_data, "ts")
    get_date_without_hour_from_timestamp(traffic_data, "ts")
    return pd.merge(traffic_data, weather_data, on="ts")

def join_hourly_data(weather_data : pd.DataFrame, traffic_data : pd.DataFrame) -> pd.DataFrame:
    """
    Joins weather and traffic data.
    """
    convert_column_to_datetime(weather_data, "ts")
    convert_column_to_datetime(traffic_data, "ts")
    get_date_hour_without_minute_from_timestamp(weather_data, "ts")
    get_date_hour_without_minute_from_timestamp(traffic_data, "ts")
    return pd.merge(traffic_data, weather_data, on="ts")

