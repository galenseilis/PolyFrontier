import json
from abc import ABC

import pandas as pd
from influxdb import InfluxDBClient

from app.etl.pipeline import AbstractPipelineProcess
from app.models.nb_cars_models import NbCrossingPredictor
from app.models.waiting_models import WaitingTimePredictor


class AbstractStoreProcess(AbstractPipelineProcess, ABC):

    def __init__(self, client):
        super().__init__()
        self.client = client


class StoreInflux(AbstractStoreProcess):

    def __init__(self, influx_client: InfluxDBClient, measurement: str):
        super().__init__(influx_client)
        self.measurement = measurement

    async def process(self, df: pd.DataFrame):
        print("Storing data to influx...")
        points = [
            {
                'measurement': self.measurement,
                'time': row.pop("ts") * 1_000_000,
                'fields': row
            } for row in json.loads(df.to_json(orient="records"))
        ]
        self.client.write_points(points)
        return df


class TrainModels(AbstractStoreProcess):

    def __init__(self, models_collection):
        super().__init__(models_collection)

    async def process(self, df: pd.DataFrame):
        models_names = ['model_waiting_in', 'model_waiting_out']
        for model_name in models_names:
            print("Loading model ", model_name, "...")
            serialized_model_future = await self.client.find_one({'name': model_name})
            serialized_model = serialized_model_future['model']

            print("Fitting model...")
            try:
                loaded_model = WaitingTimePredictor.load(serialized_model)
            except Exception:  # TODO: improve using factory
                loaded_model = NbCrossingPredictor.load(serialized_model)
            new_model_instance = loaded_model.unfitted()
            new_model_instance.fit(df)
            print("Model fitted.")
            print("Saving model...")

            await self.client.update_one({'name': model_name}, {'$set': {'model': new_model_instance.serialize()}})
            print("Model saved.")
        return df
