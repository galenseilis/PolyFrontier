import io
import json

import motor.motor_asyncio
import pandas as pd
from fastapi import FastAPI, File

from influxdb import InfluxDBClient

import logging
import time

from app.etl.pipeline import Pipeline
from app.etl.load import TrainRawModels, StoreInflux
from app.etl.transform import FilterEmpty, MergeWith, DatetimeTS, FilterForCustomsDataPerDay, KeepColumns
from app.etl.extract import CSVFileLoader

NB_CONNECTION_ATTEMPTS = 10

influx_client = None
prev_exception = None

doc = {
    'status': 'STARTED',
}

for i in range(NB_CONNECTION_ATTEMPTS):
    try:
        time.sleep(1)
        if not influx_client:
            print("Attempting to connect to influxdb...")
            influx_client = InfluxDBClient(host='influxdb', port=8086)
            influx_client.create_database('ps7-al-sd')
            influx_client.switch_database('ps7-al-sd')
            print(f"Connected {influx_client}.")
        break
    except Exception as e:
        logging.error(e)
        prev_exception = e
if not influx_client:
    raise prev_exception

mongo_client, db = None, None
prev_exception = None

doc = {
    'status': 'STARTED',
}

for i in range(NB_CONNECTION_ATTEMPTS):
    try:
        time.sleep(1)
        if not mongo_client:
            print("Attempting to connect to mongodb...")
            mongo_client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://root:ps7alsd@mongo:27017/')
            print(f"Connected {mongo_client}.")
        if not db:
            print("Fetching database...")
            db = mongo_client['ps7-al-sd']
            print(f"Connected to database {db}.")
        print("Attempting to insert base models...")
        db['status'].replace_one({'name': 'worker_batch1'},
                                 {'name': 'worker_batch1', 'state': 'RUNNING', 'connection_attempts': str(i + 1)},
                                 upsert=True)
        models_collection = db['models']
        break
    except Exception as e:
        logging.error(e)
        prev_exception = e
if not mongo_client:
    raise prev_exception

app = FastAPI()


@app.on_event("shutdown")
def shutdown_event():
    # TODO: db['status'].replace_one({'name': 'worker_batch1'}, {'name': 'worker_batch1', 'state': 'DOWN'})
    pass


@app.get("/")
async def root():
    return {"message": "Welcome to the PS7-AL-SD 2021/2022 project."}


@app.post("/speed_process/controls")
async def batch_process(file: bytes = File(...)):
    raw_columns = ["ts", "avg_nb_vehicules_in_per_hour", "nb_trucks_in", "nb_cars_in", "avg_waiting_in",
                   "avg_nb_vehicules_out_per_hour", "nb_trucks_out", "nb_cars_out", "avg_waiting_out"]
    pipeline = (
            Pipeline(file) >> CSVFileLoader() >> FilterEmpty() >> FilterForCustomsDataPerDay() >> DatetimeTS() >>
            StoreInflux(influx_client, 'raw_controls_data') >> MergeWith(influx_client, 'train_raw_data') >>
            KeepColumns(columns=raw_columns) >> TrainRawModels(models_collection) >>
            StoreInflux(influx_client, 'train_raw_data')
    )
    print("Executing ETL : ", pipeline)
    msg, _ = await pipeline.execute()
    return {"message": msg}
