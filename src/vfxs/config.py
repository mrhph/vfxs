#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import pathlib

from starlette.config import Config
from starlette.datastructures import Secret

BASE_PATH = pathlib.Path(__file__).parent.parent.parent

config = Config(BASE_PATH.joinpath('.env'))

# 环境配置信息
IS_DEBUG = config('IS_DEBUG', cast=bool, default=False)
SERVER_PORT = config('SERVER_PORT', cast=int, default=8000)
DB_HOST = config('DB_HOST', default='127.0.0.1')
DB_PORT = config('DB_PORT', default='3306')
DB_USER = config('DB_USER', default=None)
DB_PASSWORD = config('DB_PASSWORD', cast=Secret, default=None)
DB_DATABASE = config('DB_DATABASE', default=None)
DB_DRIVER = config('DB_DRIVER', default='mysql')
ASSET_EXPIRE_TIME = config('ASSET_EXPIRE_TIME_SECOND', cast=int, default=172800)

# client_id白名单
CLIENT_WHITE_LIST = set(config('CLIENT_WHITE_LIST', cast=str, default='').split(','))

# 路径信息
DATA_DIR = pathlib.Path(config('DATA_DIR', default=BASE_PATH.joinpath('data')))
LOG_DIR = pathlib.Path(config('LOG_DIR', default=BASE_PATH.joinpath('logs')))
TMP_DIR = DATA_DIR.joinpath('tmp')
MATERIAL_DIR = DATA_DIR.joinpath('material')
SQLITE_DB_FILE = pathlib.Path(__file__).parent.joinpath('sqlite3.db')

# cos配置信息
COS_SECRET_ID = config('COS_SECRET_ID', default=None)
COS_SECRET_KEY = config('COS_SECRET_KEY', default=None)
COS_APP_ID = config('COS_APP_ID', default=None)
COS_REGION = config('COS_REGION', default='ap-nanjing')
COS_BUCKET_NAME = config('COS_BUCKET_NAME', default='vfxs')
