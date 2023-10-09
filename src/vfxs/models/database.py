#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import os

from databases import Database
from sqlalchemy import MetaData
from sqlalchemy.engine.url import URL


from ..config import IS_DEBUG, DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_DATABASE, DB_DRIVER

if IS_DEBUG:
    database = Database(f"sqlite:///{os.path.join(os.path.dirname(__file__), 'sqlite.db')}")
else:
    url = URL.create(
        drivername=DB_DRIVER,
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_DATABASE,
        query={'charset': 'utf8'}
    )
    database = Database(str(url))

metadata = MetaData()

