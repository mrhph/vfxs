#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.jobstores.memory import MemoryJobStore


# 作业存储器
jobstores = {
    'default': MemoryJobStore(),  # 内存
    # 'redis': RedisJobStore(db=5, host='', port=6379)  # redis
}

# 执行器
executors = {
    'default': AsyncIOExecutor()
}

# 任务配置

job_defaults = {
    'coalesce': True,  # 错过的作业执行合并。如某任务由于某原因期间有5次未执行，当该任务调度时只会执行一次，为False会执行5次
    'max_instances': 1  # 同时执行的作业实例数
}

scheduler = AsyncIOScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults)
# repeated = AsyncIOScheduler(jobstores=jobstores, job_defaults=job_defaults)

from .jobs.task import scheduler_simple_task as func
scheduler.add_job(func, trigger='interval', seconds=2, id=func.__name__)
from .jobs.job import scheduler_stage_task as func
scheduler.add_job(func, trigger='interval', seconds=5, id=func.__name__)
