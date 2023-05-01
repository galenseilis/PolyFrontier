import json
import weathercom
from fastapi import FastAPI
from utils import mph_to_kph

app = FastAPI()

def get_temperature_in_celsius(city):
    weatherDetails = weathercom.getCityWeatherDetails(city)
    data = json.loads(weatherDetails)
    return data['vt1observation']['temperature']

def get_pressure(city):
    weatherDetails = weathercom.getCityWeatherDetails(city)
    data = json.loads(weatherDetails)
    return data['vt1observation']['altimeter']

def get_precipitation(city):
    weatherDetails = weathercom.getCityWeatherDetails(city)
    data = json.loads(weatherDetails)
    return data['vt1observation']['precip24Hour']

def get_wind_speed(city):
    weatherDetails = weathercom.getCityWeatherDetails(city)
    data = json.loads(weatherDetails)
    mph_wind_speed = data['vt1observation']['windSpeed']
    return mph_to_kph(mph_wind_speed)

def get_full_weather_details(city):
    weatherDetails = weathercom.getCityWeatherDetails(city)
    data = json.loads(weatherDetails)
    return data['vt1observation']

@app.get("/temperature/{city}")
def get_temperature(city: str):
    return get_temperature_in_celsius(city)

@app.get("/pressure/{city}")
def get_pressure_api(city: str):
    return get_pressure(city)

@app.get("/precipitation/{city}")
def get_precipitation_api(city: str):
    return get_precipitation(city)

@app.get("/wind_speed/{city}")
def get_wind_speed_api(city: str):
    return get_wind_speed(city)

@app.get("/weather/{city}")
def get_weather(city: str):
    return get_full_weather_details(city)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)