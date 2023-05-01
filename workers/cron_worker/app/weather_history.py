import numpy as np
import pandas as pd
import time
import datetime



def get_weather_history_data_by_hour_and_day(year,month,day, hour):
    date = year+'-'+month+'-'+day + ' ' + hour

    weather_history_data = pd.read_csv('dataset_custom_sample_per_hour_v1.csv')
    weather_history_data['ts'] = weather_history_data['ts'].apply(lambda x: pd.Timestamp(x).strftime('%Y-%m-%d %H'))
    weather_history_data_by_hour_and_day = weather_history_data.loc[weather_history_data['ts'] == date]

    return weather_history_data_by_hour_and_day


def weather_history_message(year,month,day,hour):
    weather_data_by_date = get_weather_history_data_by_hour_and_day(year,month,day,hour)
    message = {
        "ts": str(weather_data_by_date['ts'].values[0]),
        "avg_temperature":int(weather_data_by_date['avg_temperature'].values[0]),
        "pressure":int( weather_data_by_date['pressure'].values[0]),
        "precipitation_MM": float(weather_data_by_date['precipitation_MM'].values[0]),
        "windspeed_Kmph": int(weather_data_by_date['windspeed_Kmph'].values[0]),
    }
    return message

