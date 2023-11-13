#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
from vfxs.config import IS_DEBUG

if IS_DEBUG:
    workers = 1
else:
    workers = 4

bind = '0.0.0.0:8888'
worker_class = 'uvicorn.workers.UvicornWorker'
# 请求超时时间，默认30
timeout = 60
# 最大客户端并发数量，默认1000，只在异步下生效
worker_connections = 1000

# 日志配置
loglevel = 'info'
accesslog = '-'  # stdio
# access_log_format = '%(t)s "%(r)s" %(s)s %(M)sms %(b)s'

