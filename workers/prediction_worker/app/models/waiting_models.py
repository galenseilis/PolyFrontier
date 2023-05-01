import pandas as pd

import prophet
from prophet import Prophet
from prophet.serialize import model_to_json, model_from_json

import optuna
from sklearn.metrics import mean_absolute_error

import json
import logging

logging.getLogger('prophet').setLevel(logging.WARNING)
prophet.models.logger.setLevel("WARN")
prophet.forecaster.logger.setLevel("WARN")
optuna.logging.set_verbosity(optuna.logging.WARNING)


class WaitingTimeSplitter:

    def __init__(self, dataset: pd.DataFrame, direction):
        self.dataset = dataset
        self.direction = direction

    def __split_for_cars(self, prepared_train_df):
        prepared_train_df_nb_cars = prepared_train_df[["ds", f"nb_cars_{self.direction}"]].copy()
        prepared_train_df_nb_cars.rename(columns={f'nb_cars_{self.direction}':'y'}, inplace=True)
        return prepared_train_df_nb_cars

    def __split_for_trucks(self, prepared_train_df):
        prepared_train_df_nb_trucks = prepared_train_df[["ds", f"nb_trucks_{self.direction}"]].copy()
        prepared_train_df_nb_trucks.rename(columns={f'nb_trucks_{self.direction}':'y'}, inplace=True)
        return prepared_train_df_nb_trucks

    def __prepare_df(self, sub_dataset):
        prepared_df = sub_dataset.copy()
        prepared_df.reset_index(inplace=True, drop=True)
        prepared_df.rename(columns={'ts':'ds', f'avg_waiting_{self.direction}': 'y'}, inplace=True)
        prepared_df["ds"] = prepared_df["ds"].dt.tz_localize(None)
        return prepared_df

    def split(self, train_percentage, include_test = True):
        nb_rows = int(self.dataset.shape[0] * train_percentage)
        prepared_train_df = self.__prepare_df(self.dataset[:nb_rows])
        prepared_train_cars_df = self.__split_for_cars(prepared_train_df)
        prepared_train_trucks_df = self.__split_for_trucks(prepared_train_df)
        if not include_test:
            return prepared_train_df, prepared_train_cars_df, prepared_train_trucks_df
        prepared_test_df = self.__prepare_df(self.dataset[nb_rows:])
        prepared_test_cars_df = self.__split_for_cars(prepared_test_df)
        prepared_test_trucks_df = self.__split_for_trucks(prepared_test_df)
        return ((prepared_train_df, prepared_test_df), (prepared_train_cars_df, prepared_test_cars_df),
                (prepared_train_trucks_df, prepared_test_trucks_df))


class WaitingTimePredictor:

    def __init__(self, direction, is_fitted=False, prophet_waiting_time=None, prophet_nb_cars=None, prophet_nb_trucks=None):
        self.prophet_waiting_time = prophet_waiting_time or Prophet()
        self.prophet_nb_cars = prophet_nb_cars or Prophet()
        self.prophet_nb_trucks = prophet_nb_trucks or Prophet()
        self._regressors = set()
        self._country_holidays = set()
        self.direction = direction
        self.__is_fitted = is_fitted
        # adding default regressors
        if not self.__is_fitted:
            self.add_regressor(f'nb_trucks_{self.direction}')
            self.add_regressor(f'nb_cars_{self.direction}')

    @classmethod
    def load(cls, serialized):
        return cls(is_fitted=True, **{k: model_from_json(v) if k.startswith('prophet') else v
                                      for k, v in json.loads(serialized).items()})

    def unfitted(self):
        unfitted_clone = self.__class__(self.direction)
        for r in self._regressors:
            unfitted_clone.add_regressor(r)
        for c in self._country_holidays:
            unfitted_clone.add_country_holidays(c)
        return unfitted_clone

    def add_regressor(self, regressor):
        self.prophet_waiting_time.add_regressor(regressor)
        self._regressors.add(regressor)

    def add_country_holidays(self, country_name):
        self.prophet_waiting_time.add_country_holidays(country_name=country_name)
        self.prophet_nb_cars.add_country_holidays(country_name=country_name)
        self.prophet_nb_trucks.add_country_holidays(country_name=country_name)
        self._country_holidays.add(country_name)

    def fit(self, dataset, train_ratio=0.8):
        if self.__is_fitted:
            raise ValueError("Model already fitted.")
        dataset_splitter = WaitingTimeSplitter(dataset, self.direction)
        waiting_train_df, cars_train_df, trucks_train_df = dataset_splitter.split(train_percentage=train_ratio,
                                                                                  include_test=False)
        self.prophet_waiting_time.fit(waiting_train_df)
        self.prophet_nb_cars.fit(cars_train_df)
        self.prophet_nb_trucks.fit(trucks_train_df)
        self.__is_fitted = True

    def predict(self, date):
        ts_df = pd.DataFrame([date], columns=["ds"])
        nb_cars_prediction = self.prophet_nb_cars.predict(ts_df)[["ds", "yhat"]].rename(columns={"yhat": f"nb_cars_{self.direction}"})
        nb_trucks_prediction = self.prophet_nb_trucks.predict(ts_df)[["ds", "yhat"]].rename(
            columns={"yhat": f"nb_trucks_{self.direction}"})
        merged_predictions = nb_cars_prediction.merge(nb_trucks_prediction, on="ds")
        waiting_prediction = self.prophet_waiting_time.predict(merged_predictions)
        return waiting_prediction["yhat"].to_numpy()[0]

    def serialize(self):
        return json.dumps({
            "direction": self.direction,
            "prophet_waiting_time": model_to_json(self.prophet_waiting_time),
            "prophet_nb_cars": model_to_json(self.prophet_nb_cars),
            "prophet_nb_trucks": model_to_json(self.prophet_nb_trucks)
        })


class WaitingTimeOptimizer:

    def __init__(self, dataset: pd.DataFrame, train_ratio = 0.8, direction: str = 'minimize'):
        self.direction = direction
        self.dataset = dataset
        self.train_ratio = train_ratio

    def optimize(self, predictor: WaitingTimePredictor, regressors, n_trials):
        dataset_splitter = WaitingTimeSplitter(self.dataset, direction=predictor.direction)
        waiting_dfs, cars_dfs, trucks_dfs = dataset_splitter.split(train_percentage=self.train_ratio)

        study_waiting = optuna.create_study(direction=self.direction)
        study_waiting.optimize(lambda t : self.objective(waiting_dfs[0], waiting_dfs[1], t, regressors), n_trials=n_trials)
        predictor.prophet_waiting_time = Prophet(**study_waiting.best_params)

        study_cars = optuna.create_study(direction=self.direction)
        study_cars.optimize(lambda t : self.objective(train=cars_dfs[0], test=cars_dfs[1], trial=t), n_trials=n_trials)
        predictor.prophet_nb_cars = Prophet(**study_cars.best_params)

        study_trucks = optuna.create_study(direction=self.direction)
        study_trucks.optimize(lambda t : self.objective(train=trucks_dfs[0], test=trucks_dfs[1], trial=t), n_trials=n_trials)
        predictor.prophet_nb_trucks = Prophet(**study_trucks.best_params)

    @staticmethod
    def objective(train, test, trial, regressors = None):
        params = {
            'changepoint_prior_scale': trial.suggest_float('changepoint_prior_scale', 0.005, 5),
            'changepoint_range': trial.suggest_float('changepoint_range', 0.8, 0.9),
            'seasonality_prior_scale': trial.suggest_float('seasonality_prior_scale', 0.1, 10),
            'holidays_prior_scale': trial.suggest_float('holidays_prior_scale', 0.1, 10),
            'seasonality_mode': trial.suggest_categorical('seasonality_mode', ['multiplicative', 'additive']),
            # 'growth': trial.suggest_categorical('growth', ['linear', 'logistic']), => ValueError: Capacities must be supplied for logistic growth in column "cap"
            'growth': trial.suggest_categorical('growth', ['linear']),
            'weekly_seasonality': trial.suggest_int('weekly_seasonality', 5, 10),
            'yearly_seasonality': trial.suggest_int('yearly_seasonality', 1, 20)
        }
        m = Prophet(**params)
        m.add_country_holidays(country_name='FR')
        if regressors:
            for r in regressors:
                m.add_regressor(r)
        m.fit(train)
        predictions = m.predict(test)
        mae_score = mean_absolute_error(test['y'], predictions['yhat'])
        return mae_score

