import os
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler(timezone="Asia/Shanghai")


async def delete_file(file: str):
    if os.path.exists(file):
        os.remove(file)


def add_delete_file_job(file: str, seconds: int = 60 * 60):
    if job := scheduler.get_job(f"df_{file}"):
        job.remove()
    scheduler.add_job(
        delete_file,
        "date",
        run_date=datetime.now() + timedelta(seconds=seconds),
        args=(file,),
        id=f"df_{file}",
        name=f"df_{file}",
    )
