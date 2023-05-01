import io
import json

import motor.motor_asyncio
import pandas as pd
from fastapi import FastAPI, File

from influxdb import InfluxDBClient

import logging
import time

from app.etl.pipeline import Pipeline
from app.etl.load import TrainModels, StoreInflux
from app.etl.transform import FilterEmpty, MergeWith, DatetimeTS, FilterForCustomsDataPerDay
from app.etl.extract import CSVFileLoader

from app.models.nb_cars_models import NbCrossingPredictor
from app.models.waiting_models import WaitingTimePredictor, WaitingTimeWeatherPredictor
from app.utils.date_manager import parse_influx_datetime, convert_column_to_datetime

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
                                 {'name': 'worker_batch1', 'state': 'RUNNING', 'connection_attempts': str(i+1)},
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


@app.post("/batch_process/controls")
async def batch_process(file: bytes = File(...)):
    pipeline = (
            Pipeline(file) >> CSVFileLoader() >> FilterEmpty() >> FilterForCustomsDataPerDay() >> DatetimeTS() >>
            StoreInflux(influx_client, 'raw_controls_data') >> MergeWith(influx_client, 'raw_meteo_data') >>  # TODO: implement weather part to merge
            MergeWith(influx_client, 'train_data') >> TrainModels(models_collection) >>
            StoreInflux(influx_client, 'train_data')
    )
    print("Executing ETL : ", pipeline)
    msg, _ = await pipeline.execute()
    return {"message": msg}


@app.post("/batch_process_weather/")
async def batch_process_weather(file: bytes = File(...)):
    new_train_df = pd.read_csv(io.StringIO(str(file, 'utf-8')), encoding='utf-8')
    if new_train_df.empty:
        return {"message": "no process. empty file."}
    convert_column_to_datetime(new_train_df, "ts")

    stored_train = influx_client.query('SELECT * FROM train_data_weather')
    stored_train = stored_train.raw["series"][0] if stored_train.raw["series"] else {}
    stored_train_df = pd.DataFrame(stored_train["values"], columns=stored_train["columns"]) \
        if stored_train else pd.DataFrame(columns=new_train_df.columns)
    stored_train_df = stored_train_df.rename(columns={'time': 'ts'})
    parse_influx_datetime(stored_train_df, 'ts')

    stored_train_df.info()
    new_train_df.info()
    train_df = pd.concat([stored_train_df, new_train_df])

    models_names = ['model_waiting_in_weather'] #, 'model_waiting_out_weather']
    for model_name in models_names:
        print("Loading model ", model_name, "...")
        serialized_model_future = await models_collection.find_one({'name': model_name})
        print(serialized_model_future)
        serialized_model = serialized_model_future['model']
        print(type(serialized_model))
        print(serialized_model)

        print("Fitting model...")
        try:
            loaded_model = WaitingTimeWeatherPredictor.load(serialized_model)
        except Exception:  # TODO: improve using factory
            loaded_model = NbCrossingPredictor.load(serialized_model)
        new_model_instance = loaded_model.unfitted()
        new_model_instance.fit(train_df)
        print("Model fitted.")
        print("Saving model...")

        await models_collection.update_one({'name': model_name}, {'$set':  {'model': new_model_instance.serialize()}})
        print("Model saved.")

        print("Inserting new train_data...")
        points = [
            {
                'measurement': 'train_data_weather',
                'time': row.pop("ts") * 1_000_000,
                'fields': row
            } for row in json.loads(train_df.to_json(orient="records"))
        ]
        influx_client.write_points(points)
        print("Train data inserted.")

    return {"message": "ok"}
