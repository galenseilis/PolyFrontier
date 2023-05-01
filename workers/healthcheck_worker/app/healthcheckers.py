import abc
import logging

import requests
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.job import Job
from typing import Dict, Optional

from influxdb import DataFrameClient

from app.data_recovery import AbstractDataRecoverer, InfluxDataRecoverer, SummaryLossReport


logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.INFO)


class AbstractHealthChecker(abc.ABC):

    def __init__(self, scheduler: AsyncIOScheduler, data_recoverer: AbstractDataRecoverer,
                 host: str, port: int, ping_interval: int):
        self._scheduler = scheduler
        self.__is_scheduled = False
        self._data_recoverer = data_recoverer
        self.jobs: Dict[str, Optional[Job]] = {'check_status': None, 'wait_for_database': None}
        self.host = host
        self.port = port
        self.ping_interval = ping_interval

    async def _schedule(self, job_key, job_func):
        self.jobs[job_key] = self._scheduler.add_job(job_func, 'interval', seconds=self.ping_interval)

    async def schedule(self):
        if not self.__is_scheduled:
            await self._schedule('check_status', self._check_status)
            self.__is_scheduled = True

    async def stop(self):
        if not self.__is_scheduled:
            return
        for j in self.jobs.values():
            if j:
                j.remove()

    @abc.abstractmethod
    async def ping(self) -> requests.Response:
        pass

    @abc.abstractmethod
    async def _check_status(self):
        pass

    @abc.abstractmethod
    async def _recover_if_needed(self):
        pass

    @abc.abstractmethod
    async def _wait_for_database(self):
        pass


class InfluxHealthChecker(AbstractHealthChecker):

    def __init__(self, scheduler: AsyncIOScheduler, host: str, port: int, ping_interval: int):
        super().__init__(scheduler, InfluxDataRecoverer(), host, port, ping_interval)
        self.ping_url = f"http://{host}:{port}/health"

    async def ping(self) -> requests.Response:
        return requests.get(self.ping_url)

    async def _recover_if_needed(self):
        losses_report: SummaryLossReport = await self._data_recoverer.evaluate_losses()
        logger.info("losses report : %s", losses_report)
        if losses_report.average_loss_percentage == 0:
            return
        await self._data_recoverer.seed_database(losses_report, 0)

    async def _wait_for_database(self):
        try:
            ping = await self.ping()
            if ping.status_code != 200:
                logger.info("Waiting for InfluxDB to be healthy...")
                return
        except requests.exceptions.ConnectionError:
            logger.info("Waiting for InfluxDB to be up...")
            return
        logger.info("InfluxDB is up... Checking for eventual data loss...")
        try:
            self._data_recoverer.client = DataFrameClient(host=self.host, port=self.port)
        except:
            logger.warning("InfluxDB connection failed...")
            return
        await self._recover_if_needed()
        self.jobs['wait_for_database'].pause()
        self.jobs['check_status'].resume()

    async def _check_status(self):
        try:
            ping = await self.ping()
            if ping.status_code == 200:
                return
            logger.warning("InfluxDB is unhealthy... Entering recovery mode...")
        except requests.exceptions.ConnectionError:
            logger.warning("InfluxDB is down... Entering recovery mode...")
        self.jobs['check_status'].pause()
        if not self.jobs['wait_for_database']:
            await self._schedule('wait_for_database', self._wait_for_database)
        else:
            self.jobs['wait_for_database'].resume()
