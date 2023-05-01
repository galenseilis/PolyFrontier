import abc
import json

import pandas as pd
from influxdb import DataFrameClient
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import Optional, Any, cast, Dict


class TableLossReport(BaseModel):
    table: str
    loss_count: int
    loss_percentage: int


class SummaryLossReport:

    def __init__(self, reports: Dict[str, TableLossReport]):
        self.reports = reports
        self.average_loss_percentage = sum(r.loss_percentage for r in self.reports.values()) / len(self.reports)

    def __str__(self):
        return f"SummaryLossReport[average_loss_percentage={self.average_loss_percentage}, " \
               f"{[str(r) for r in self.reports.items()]}"


class AbstractDataRecoverer(abc.ABC):

    def __init__(self, client: Any = None):
        self.client: Optional[Any] = client

    async def _requires_client(self):
        if not self.client:
            raise ValueError("Data recoverer requires a client.")

    @abc.abstractmethod
    async def evaluate_losses(self) -> SummaryLossReport:
        pass

    @abc.abstractmethod
    async def seed_database(self, summary_loss_report: SummaryLossReport, avg_loss_threshold: int):
        pass


class InfluxDataRecoverer(AbstractDataRecoverer):

    def __init__(self, client: DataFrameClient = None):
        super().__init__(client)

    async def evaluate_losses(self) -> SummaryLossReport:
        await self._requires_client()
        influx_client = cast(DataFrameClient, self.client)
        try:
            influx_client.create_database('ps7-al-sd')
        except:
            pass
        finally:
            influx_client.switch_database('ps7-al-sd')
        with open('app/data/initial_metrics.json') as f:
            expected_metrics = json.load(f)
        table_loss_reports = {}
        for measurement in ('raw_controls_data', 'raw_meteo_data', 'train_data'):
            influx_result = influx_client.query(f'SELECT * FROM {measurement}', raise_errors=False)
            stored_df: pd.DataFrame = influx_result.get(measurement, pd.DataFrame())
            expected_stored_count = expected_metrics['counts'][measurement]
            if expected_stored_count == 0:
                loss_report_for_measurement = TableLossReport(table=measurement, loss_count=0, loss_percentage=0)
            elif stored_df.empty:
                loss_report_for_measurement = TableLossReport(table=measurement, loss_count=expected_stored_count,
                                                              loss_percentage=100)
            else:
                current_base_count = min(len(stored_df.index), expected_stored_count)
                loss = expected_stored_count - current_base_count
                loss_percentage = 100 - current_base_count * 100 / expected_stored_count
                loss_report_for_measurement = TableLossReport(table=measurement, loss_count=loss,
                                                              loss_percentage=loss_percentage)
            del stored_df
            table_loss_reports[measurement] = loss_report_for_measurement
        return SummaryLossReport(table_loss_reports)

    async def seed_database(self, summary_loss_report: SummaryLossReport, avg_loss_threshold: int) -> None:
        await self._requires_client()
        influx_client = cast(DataFrameClient, self.client)
        for measurement in ('raw_controls_data', 'raw_meteo_data', 'train_data'):
            backup_dataframe = pd.read_csv(f'app/data/{measurement}.backup.csv')
            backup_dataframe["ts"] = pd.to_datetime(backup_dataframe["ts"], utc=True)
            backup_dataframe = backup_dataframe.set_index("ts")
            influx_client.write_points(backup_dataframe, measurement)


class MongoDataRecoverer(AbstractDataRecoverer):

    def __init__(self, client: AsyncIOMotorClient = None):
        super().__init__(client)

    async def evaluate_losses(self):
        await self._requires_client()
        pass

    async def seed_database(self, summary_loss_report: SummaryLossReport, avg_loss_threshold: int):
        await self._requires_client()
        pass
