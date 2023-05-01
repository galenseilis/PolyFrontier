from fastapi import FastAPI
import motor.motor_asyncio
from typing import Optional

from app.data_handler import load_models
from app.date_manager import get_date_from_date_month_year, get_this_year, get_datetime_from_date_month_year_hour

import time

from app.models.nb_cars_models import NbCrossingPredictor
from app.models.waiting_models import WaitingTimePredictor

NB_MONGO_ATTEMPTS = 10

mongo_client, db = None, None
prev_exception = None

doc = {
    'status': 'STARTED',
}

for i in range(NB_MONGO_ATTEMPTS):
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
        db['status'].replace_one({'name': 'worker_prediction1'},
                                 {'name': 'worker_prediction1', 'state': 'RUNNING', 'connection_attempts': str(i + 1)},
                                 upsert=True)
        models_collection = db['models']
        for name, model in load_models():
            models_collection.replace_one({'name': name}, {'name': name, 'model': model}, upsert=True)
        break
    except Exception as e:
        print(e)
        prev_exception = e
if not mongo_client:
    raise prev_exception

app = FastAPI()


@app.on_event("shutdown")
def shutdown_event():
    # TODO: db['status'].replace_one({'name': 'worker_prediction1'}, {'name': 'worker_batch1', 'state': 'SHUTDOWN'})
    pass


@app.get("/")
async def root():
    return {"message": "Welcome to the PS7-AL-SD 2021/2022 project."}


@app.get("/predict-waiting-time")
async def predict_waiting_time(direction: str, day: int, month: int, year: Optional[int] = None,
                               hour: Optional[int] = None, weather: bool = False):
    # weather can be 0,1 or false,true or False,True or off,on
    print("predict_waiting_time_in")
    if direction not in ["in", "out"]:
        raise ValueError(f"Unsupported direction [{direction}]")
    if year is None:
        year = get_this_year()
    model_name = f'model_waiting_{direction}'
    if hour is not None:
        model_name += "_hours"
    if weather:
        model_name += "_weather"
    print("Loading model ", model_name)
    serialized_model_future = await models_collection.find_one({'name': model_name})
    serialized_model = serialized_model_future['model']
    loaded_model = WaitingTimePredictor.load(serialized_model)
    date = get_date_from_date_month_year(day, month, year) if hour is None else \
        get_datetime_from_date_month_year_hour(day, month, year, hour)
    print("Predicting for date ", date)
    predicted_prediction = loaded_model.predict(date)
    print("Prediction result => ", predicted_prediction)
    return {f"average waiting time ({direction})": predicted_prediction}


@app.get("/predict-number-cars")
async def predict_number_cars(direction: str, day: int, month: int, year: Optional[int] = None,
                              hour: Optional[int] = None):
    print("predict_number_cars")
    if year is None:
        year = get_this_year()
    model_name = f'model_nb_cars_{direction}'
    if hour is not None:
        model_name += "_hours"
    print("Loading model ", model_name)
    serialized_model_future = await models_collection.find_one({'name': model_name})
    serialized_model = serialized_model_future['model']
    loaded_model = NbCrossingPredictor.load(serialized_model)
    date = get_date_from_date_month_year(day, month, year) if hour is None else \
        get_datetime_from_date_month_year_hour(day, month, year, hour)
    print("Predicting for date ", date)
    predicted_prediction = loaded_model.predict(date)
    print("Prediction result => ", predicted_prediction)
    return {f"average number cars ({direction})": predicted_prediction}


@app.get("/predict-number-trucks")
async def predict_number_trucks(direction: str, day: int, month: int, year: Optional[int] = None,
                                hour: Optional[int] = None):
    print("predict_number_trucks")
    if year is None:
        year = get_this_year()
    model_name = f'model_nb_trucks_{direction}'
    if hour is not None:
        model_name += "_hours"
    print("Loading model ", model_name)
    serialized_model_future = await models_collection.find_one({'name': model_name})
    serialized_model = serialized_model_future['model']
    loaded_model = NbCrossingPredictor.load(serialized_model)
    date = get_date_from_date_month_year(day, month, year) if hour is None else \
        get_datetime_from_date_month_year_hour(day, month, year, hour)
    print("Predicting for date ", date)
    predicted_prediction = loaded_model.predict(date)
    print("Prediction result => ", predicted_prediction)
    return {f"average number trucks ({direction})": predicted_prediction}
