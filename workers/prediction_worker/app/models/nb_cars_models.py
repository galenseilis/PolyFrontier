import pandas as pd
from prophet import Prophet
from prophet.serialize import model_to_json, model_from_json

import json

from app.models.waiting_models import WaitingTimeSplitter


class NbCrossingPredictor:

    def __init__(self, direction, type_vehicule, is_fitted=False, prophet_nb_cars=None):
        self.prophet_nb_cars = prophet_nb_cars or Prophet()
        self._country_holidays = set()
        self.direction = direction
        self.type_vehicule = type_vehicule
        self.is_fitted = is_fitted

    @classmethod
    def load(cls, serialized):
        return cls(is_fitted=True, **{k: model_from_json(v) if k.startswith('prophet') else v
                                      for k, v in json.loads(serialized).items()})

    def unfitted(self):
        unfitted_clone = self.__class__(self.direction)
        for c in self._country_holidays:
            unfitted_clone.add_country_holidays(c)
        return unfitted_clone

    def add_country_holidays(self, country_name):
        self.prophet_nb_cars.add_country_holidays(country_name=country_name)

    def fit(self, dataset, train_ratio=0.8):
        dataset_splitter = WaitingTimeSplitter(dataset, direction=self.direction)
        _, cars_train_df, trucks_train_df = dataset_splitter.split(train_percentage=train_ratio, include_test=False)
        self.prophet_nb_cars.fit(cars_train_df if self.type_vehicule == 'cars' else trucks_train_df)  # TODO: to improve
        self.is_fitted = True

    def predict(self, date):
        ts_df = pd.DataFrame([date], columns=["ds"])
        nb_cars_prediction = self.prophet_nb_cars.predict(ts_df)
        return nb_cars_prediction["yhat"].to_numpy()[0]

    def serialize(self):
        return json.dumps({
            "direction": self.direction,
            "type_vehicule": self.type_vehicule,
            "prophet_nb_cars": model_to_json(self.prophet_nb_cars)
        })
