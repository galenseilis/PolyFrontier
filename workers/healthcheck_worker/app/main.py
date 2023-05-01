from fastapi import FastAPI
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.healthcheckers import InfluxHealthChecker

app = FastAPI()
async_scheduler = AsyncIOScheduler()

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.INFO)

influx_health_checker = InfluxHealthChecker(async_scheduler, 'influxdb', 8086, 5)


@app.on_event("startup")
async def startup_event():
    # TODO: db['status'].replace_one({'name': 'worker_batch1'}, {'name': 'worker_batch1', 'state': 'DOWN'})
    """db['status'].replace_one({'name': 'worker_healthcheck1'},
                             {'name': 'worker_healthcheck1', 'state': 'RUNNING', 'connection_attempts': str(i + 1)},
                             upsert=True)"""
    async_scheduler.start()
    await influx_health_checker.schedule()


@app.on_event("shutdown")
async def shutdown_event():
    # TODO: db['status'].replace_one({'name': 'worker_batch1'}, {'name': 'worker_batch1', 'state': 'DOWN'})
    await influx_health_checker.stop()
    async_scheduler.start()


@app.get("/")
async def root():
    return {"message": "Welcome to the PS7-AL-SD 2021/2022 project."}
