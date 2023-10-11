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
DB_HOST = config('DB_HOST', default='127.0.0.1')
DB_PORT = config('DB_PORT', default='3306')
DB_USER = config('DB_USER', default=None)
DB_PASSWORD = config('DB_PASSWORD', cast=Secret, default=None)
DB_DATABASE = config('DB_DATABASE', default=None)
DB_DRIVER = config('DB_DRIVER', default='mysql')
ASSET_EXPIRE_TIME = config('ASSET_EXPIRE_TIME', cast=int, default=172800)

# 路径信息
DATA_DIR = pathlib.Path(config('DATA_DIR', default=BASE_PATH.joinpath('data')))
SQLITE_DB_FILE = pathlib.Path(__file__).parent.joinpath('sqlite3.db')


if __name__ == '__main__':
    print(IS_DEBUG)
    print(BASE_PATH)
    print(DATA_DIR)
    print(SQLITE_DB_FILE)
