#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import os
import time

import aiofiles
import sqlalchemy as sa
from fastapi import UploadFile, Form, Request
from starlette.datastructures import UploadFile as StarletteUploadFile

from . import router
from ...config import DATA_DIR
from ...models.database import database
from ...models.tables import material

ASSET_EXPIRE_TIME = 3600 * 48  # 2day


@router.post('/zone/{zone}/asset')
async def asset_upload(zone: str, request: Request):
    form = await request.form()
    values, sqls = list(), list()
    for k, file in form.items():
        if not isinstance(file, StarletteUploadFile):
            continue
        path = DATA_DIR.joinpath(f'{zone}_{file.filename}')
        async with aiofiles.open(path, 'wb') as fp:
            await fp.write(await file.read())
        name, ft = file.filename.rsplit('.', 1)
        current_time = int(time.time() * 1000)
        record = {
            'name': name,
            'filename': file.filename,
            'type': 'pretreatment',
            'zone': zone,
            'storage': {'type': 'systemFile', 'info': {'path': str(path), 'size': file.size}},
            'save_time': current_time,
            'expire_time': ASSET_EXPIRE_TIME,
            'create_time': current_time,
            'is_delete': False,
        }
        values.append(record)
        sqls.append(sa.insert(material).values(record))
        # await database.execute(sa.insert(material).values(record))
    if sqls:
        await database.execute_many(sa.insert(material), values)
    response = [{'name': i['name'], 'size': i['storage']['info']['size']} for i in values]
    return response


@router.get('/zone/{zone}/asset')
async def get_asset(zone: str, typeof: str = 'pretreatment'):
    print(typeof)
    if typeof != 'pretreatment':
        return ''
    sql = sa.select(
        material.c.name, material.c.storage
    ).where(material.c.zone == zone, material.c.type == typeof)
    data = await database.fetch_all(sql)
    response = [{'name': i.name, 'size': i.storage['info']['size']} for i in data]
    return response


@router.post('/zone/{zone}/synth/oneshot')
async def synth_oneshot(zone: str, files: list[UploadFile], rules: str = Form()):
    pass
