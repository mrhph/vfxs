#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import logging
from importlib.metadata import entry_points

from fastapi import FastAPI
from fastapi.exceptions import HTTPException

from vfxs.models.database import database
from vfxs.utils.enums import ResponseCode
from vfxs.utils.response import jsonify

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


async def exception_handler(request, exc):
    message = str(getattr(exc, 'detail', exc))
    status_code = getattr(exc, 'status_code', 500)
    return jsonify(code=ResponseCode.E10100, message=message, status_code=status_code)


async def status_code_handler(request, exc):
    return jsonify(code=ResponseCode.E10100, message=str(exc.detail), status_code=exc.status_code)


def get_app():
    app = FastAPI()
    load_modules(app)
    app.add_exception_handler(HTTPException, exception_handler)
    app.add_exception_handler(Exception, exception_handler)
    app.add_exception_handler(404, status_code_handler)
    app.add_exception_handler(405, status_code_handler)
    app.add_event_handler('startup', app_startup)
    app.add_event_handler('shutdown', app_shutdown)
    return app


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(get_app())
