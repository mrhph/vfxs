#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
from fastapi import APIRouter

router = APIRouter()


def init_app(app):
    from . import views
    app.include_router(router, prefix='/v1.0')
