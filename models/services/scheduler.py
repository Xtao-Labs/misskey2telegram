import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler(timezone="Asia/ShangHai")


async def delete_file(file: str):
    if os.path.exists(file):
        os.remove(file)


def add_delete_file_job(file: str, seconds: int = 10 * 60):
    if job := scheduler.get_job(f"df_{file}"):
        job.remove()
    scheduler.add_job(delete_file, "interval", args=[file], seconds=seconds, id=f"df_{file}")
