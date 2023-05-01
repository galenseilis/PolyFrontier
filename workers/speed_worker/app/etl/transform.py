import pandas as pd
from influxdb import InfluxDBClient
from typing import Union

from app.etl.pipeline import AbstractPipelineProcess, PipelineInterruption
from app.utils.date_manager import convert_column_to_datetime, parse_influx_datetime


class FilterEmpty(AbstractPipelineProcess):

    async def process(self, df: pd.DataFrame):
        if df.empty:
            raise PipelineInterruption("no process. empty file.")
        df.info()
        return df


class FilterForCustomsDataPerDay(AbstractPipelineProcess):

    def __init__(self, high_bound_waiting_time: Union[int, float] = 360,
                 high_bound_number_vehicules: Union[int, float] = 10_000):
        super().__init__()
        self.high_bound_waiting_time = high_bound_waiting_time
        self.high_bound_number_vehicules = high_bound_number_vehicules

    async def process(self, df: pd.DataFrame):
        print("Filtering data for unusual values...")
        columns_name = df.columns
        for i in range(1, len(columns_name)):
            if columns_name[i] == 'avg_waiting_in' or columns_name[i] == 'avg_waiting_out':
                df = df.loc[(df[columns_name[i]] <= self.high_bound_waiting_time) & (df[columns_name[i]] >= 0)]
            else:
                df = df.loc[(df[columns_name[i]] <= self.high_bound_number_vehicules) & (df[columns_name[i]] >= 0)]
        return df


class FilterForCustomsDataPerHour(FilterForCustomsDataPerDay):

    def __init__(self):
        super().__init__(high_bound_number_vehicules=10_000 / 24)


class FilterForWeatherData(AbstractPipelineProcess):

    def __init__(self):
        super().__init__()
        self.avg_temperature_low_bound = -25
        self.avg_temperature_high_bound = 45
        self.pressure_low_bound = 950
        self.pressure_high_bound = 1050
        self.windspeed_low_bound = 0
        self.windspeed_high_bound = 250
        self.precipitaion_MM_low_bound = 0
        self.precipitaion_MM_high_bound = 200

    async def process(self, df: pd.DataFrame):
        print("Filtering data for unusual values...")
        columns_name = df.columns
        for i in range(1, len(columns_name)):
            if columns_name[i] == "avg_temperature":
                df = df.loc[(df[columns_name[i]] <= self.avg_temperature_high_bound) &
                            (df[columns_name[i]] >= self.avg_temperature_low_bound)]
            elif columns_name[i] == "pressure":
                df = df.loc[(df[columns_name[i]] <= self.pressure_high_bound) &
                            (df[columns_name[i]] >= self.pressure_low_bound)]
            elif columns_name[i] == "windspeed":
                df = df.loc[(df[columns_name[i]] <= self.windspeed_high_bound) &
                            (df[columns_name[i]] >= self.windspeed_low_bound)]
            elif columns_name[i] == "precipitaion_MM":
                df = df.loc[(df[columns_name[i]] <= self.precipitaion_MM_high_bound) &
                            (df[columns_name[i]] >= self.precipitaion_MM_low_bound)]
        return df


class DatetimeTS(AbstractPipelineProcess):

    async def process(self, df: pd.DataFrame):
        print("Converting ts values to datetime...")
        convert_column_to_datetime(df, "ts")
        return df


class MergeWith(AbstractPipelineProcess):

    def __init__(self, influx_client: InfluxDBClient, measurement: str):
        super().__init__()
        self.influx_client: InfluxDBClient = influx_client
        self.measurement: str = measurement

    def __str__(self):
        return f"{self.__class__.__name__}[{self.measurement}]"

    async def process(self, new_train_df: pd.DataFrame):
        print(f"Merging with {self.measurement}...")
        to_merge_with = self.influx_client.query(f'SELECT * FROM {self.measurement}')
        to_merge_with = to_merge_with.raw["series"][0] if to_merge_with.raw["series"] else {}
        if not to_merge_with:
            return new_train_df
        to_merge_with_df = pd.DataFrame(to_merge_with["values"], columns=to_merge_with["columns"])
        to_merge_with_df = to_merge_with_df.rename(columns={'time': 'ts'})
        parse_influx_datetime(to_merge_with_df, 'ts')
        return new_train_df.set_index('ts').combine_first(to_merge_with_df.set_index('ts')).reset_index()


class KeepColumns(AbstractPipelineProcess):

    def __init__(self, columns):
        super().__init__()
        self.columns = columns

    def __str__(self):
        return f"{self.__class__.__name__}[{self.columns}]"

    async def process(self, df: pd.DataFrame):
        print(f"Filtering columns...")
        return df[self.columns]
