#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import logging
import time
import traceback
from importlib.metadata import entry_points

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from fastapi.routing import APIRoute
from starlette.types import Scope, Receive, Send

from vfxs.config import DATA_DIR, LOG_DIR, TMP_DIR, MATERIAL_DIR, SERVER_PORT
from vfxs.models.database import database
from vfxs.utils.enums import ResponseCode
from vfxs.utils.logger import LOGGER
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


async def exception_handler(request: Request, exc):
    message = str(getattr(exc, 'detail', exc))
    status_code = getattr(exc, 'status_code', 500)
    LOGGER.error(f'{request.method} {request.url} 异常, {exc.__class__.__name__}: {message}')
    LOGGER.error(traceback.format_exc())
    return jsonify(code=ResponseCode.E10100, message=message, status_code=status_code)


async def status_code_handler(request: Request, exc):
    LOGGER.error(f'{request.method} {request.url} 异常, {exc.__class__.__name__}: {str(exc.detail)}')
    LOGGER.error(traceback.format_exc())
    return jsonify(code=ResponseCode.E10100, message=str(exc.detail), status_code=exc.status_code)


class RouteClass(APIRoute):

    async def handle(self, scope: Scope, receive: Receive, send: Send) -> None:
        start = int(time.time() * 1000)
        await super().handle(scope, receive, send)
        end = int(time.time() * 1000)
        LOGGER.debug(f'{scope["client"][0]}:{scope["client"][1]} - {scope["method"]} {scope["path"]} '
                     f'{scope["type"].upper()}/{scope["http_version"]} cost: {end - start}ms')


def get_app():
    app = FastAPI()

    @app.get('/')
    def index():
        return jsonify(code=ResponseCode.E0, message='vfxs', status_code=200)

    load_modules(app)
    app.add_exception_handler(HTTPException, exception_handler)
    app.add_exception_handler(Exception, exception_handler)
    app.add_exception_handler(404, status_code_handler)
    app.add_exception_handler(405, status_code_handler)
    app.add_event_handler('startup', app_startup)
    app.add_event_handler('shutdown', app_shutdown)
    return app


def server_startup():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    TMP_DIR.mkdir(parents=True, exist_ok=True)
    MATERIAL_DIR.mkdir(parents=True, exist_ok=True)
    # 生成模型的engine文件
    from vfxs.vfx import VFXViewfinderSlowAction
    VFXViewfinderSlowAction('', '')


if __name__ == '__main__':
    import uvicorn
    server_startup()
    LOGGER.info('启动server')
    uvicorn.run(get_app(), host='0.0.0.0', port=SERVER_PORT)
