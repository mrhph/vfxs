#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import logging
from importlib.metadata import entry_points

from fastapi import FastAPI

from vfxs.models.database import database

logger = logging.getLogger(__name__)


def load_modules(app):
    for ep in entry_points()["vfxs.modules"]:
        logger.info("Loading module: %s", ep.name)
        mod = ep.load()
        init_app = getattr(mod, "init_app", None)
        if init_app:
            init_app(app)


async def app_startup():
    await database.connect()


async def app_shutdown():
    await database.disconnect()


def get_app():
    app = FastAPI()
    load_modules(app)
    app.add_event_handler('startup', app_startup)
    app.add_event_handler('shutdown', app_shutdown)
    return app


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(get_app())
