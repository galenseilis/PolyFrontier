import requests
import json



from app.date_manager import format_date, get_date_from_timestamp


def get_forcast_weather_data():
    url = 'http://api.weatherapi.com/v1/forecast.json?key=c2a16b4e4c7943dcb89175227220601&q=Calais&days=7&aqi=no&alerts=no'
    resp = requests.get(url=url)
    data_list=[]
    data = resp.json()
    forecast_data = data['forecast']['forecastday']
    for _day in forecast_data:
         data_list.append((_day['date'],_day['hour']))
    dict_day_data = dict(data_list)
    return dict_day_data



def generate_weather_data_message():
    message = []
    response = get_forcast_weather_data()
    for _day in response.keys():
        data = {
            "ts": _day,
            "avg_temperature": response[_day][11]['temp_c'],
            "pressure": response[_day][11]['pressure_mb'],
            "precipitation_MM": response[_day][11]['precip_mm'],
            "windspeed_Kmph": response[_day][11]['wind_kph']
        }
        message.append(data)
    return message

def generate_weather_hourly_data_message():
    message = []
    response = get_forcast_weather_data()
    for _day in response.keys():
        for _hour in range(len(response[_day])):
            timestamp = str(get_date_from_timestamp(response[_day][_hour]['time_epoch']))
            data = {
                "ts": timestamp,
                "avg_temperature": response[_day][_hour]['temp_c'],
                "pressure": response[_day][_hour]['pressure_mb'],
                "precipitation_MM": response[_day][_hour]['precip_mm'],
                "windspeed_Kmph": response[_day][_hour]['wind_kph']
            }
            message.append(data)
    return message




