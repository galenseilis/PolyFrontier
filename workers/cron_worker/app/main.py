import asyncio
from datetime import datetime
from time import sleep
import requests
import pandas as pd
import uvicorn
from fastapi import FastAPI
from typing import Optional
from retrying import retry


from app.date_manager import get_this_year

from app.generate_mock_data import MockDataGenerator
import json

import nest_asyncio

from app.weather_forcast import generate_weather_data_message, generate_weather_hourly_data_message
from app.weather_history import weather_history_message

nest_asyncio.apply()

TIME_INTERVAL_IN_SEC = 5
URL_RECEIVER = "http://batch_worker_1:80/batch_process/meteo"
csv = "data.csv"

mock = MockDataGenerator()

app = FastAPI()
# TODO: check https://gist.github.com/codemation/185754db70deffac652bb9a3c2b46ed0


# TODO: register to mongoDB status


async def generate_message(i):
    now = datetime.now()
    raw_data = mock.generate_for_date(datetime(now.year, now.month, now.day + i, now.hour))
    print(raw_data)
    message = {
        "ts": raw_data[0],
        "avg_nb_vehicules_in_per_hour": raw_data[1],
        "nb_trucks_in": raw_data[2],
        "nb_cars_in": raw_data[3],
        "avg_waiting_in": raw_data[4],
        "avg_nb_vehicules_out_per_hour": raw_data[5],
        "nb_trucks_out": raw_data[6],
        "nb_cars_out": raw_data[7],
        "avg_waiting_out": raw_data[8]
    }
    return message


async def generate_csv():
    messages = []
    for i in range(10):
        message = await generate_message(i)
        messages.append(message)
    df = pd.read_json(json.dumps(messages))
    print("generating ", df)
    df.to_csv("data.csv", index=False)


@app.get("/send/")
async def star_tasks():
    await generate_csv()
    with open(csv, 'rb') as f:
        try:
            print("Sending fresh data to ", URL_RECEIVER)
            requests.post(URL_RECEIVER, files={"file": f})
        except requests.exceptions.ConnectionError as e:
            print("Failed to send data to ", URL_RECEIVER)
            print(e)


@app.on_event("shutdown")
def shutdown_event():
    # TODO: db['status'].replace_one({'name': 'worker_batch1'}, {'name': 'worker_batch1', 'state': 'DOWN'})
    pass


@app.get("/")
async def root():
    return {"message": "Welcome to the PS7-AL-SD 2021/2022 psroject."}


@app.get("/weather")
@retry(stop_max_attempt_number=3,wait_random_min=2000,wait_random_max=6000)
def get_weather():
    weather_message = generate_weather_data_message()
    dfItem = pd.DataFrame.from_records(weather_message)
    print("generating ", dfItem)
    dfItem.to_csv("forcast_weather_data.csv", index=False)

@app.get("/weather-hourly")
@retry(stop_max_attempt_number=3,wait_random_min=2000,wait_random_max=6000)
def get_weather_hourly():
    weather_message = generate_weather_hourly_data_message()
    dfItem = pd.DataFrame.from_records(weather_message)
    dfItem.to_csv("forcast_hourly_weather_data.csv", index=False)


@app.get("/history-weather")
@retry(stop_max_attempt_number=3,wait_random_min=2000,wait_random_max=6000)
def get_history_weather(day:str, month:str, year:str,hour:str):
    history_weather_message = weather_history_message(year,month,day,hour)
    df = pd.DataFrame(history_weather_message,index=[0])
    df.to_csv("history_weather_data.csv", index=False)



if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8080)