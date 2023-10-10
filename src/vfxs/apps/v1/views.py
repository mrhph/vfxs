#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import time

import aiofiles
import sqlalchemy as sa
from fastapi import UploadFile, Form, Request
from fastapi.responses import JSONResponse
from starlette.datastructures import UploadFile as StarletteUploadFile

from vfxs.config import ASSET_EXPIRE_TIME, DATA_DIR
from vfxs.models import database, material
from vfxs.utils.request import paras_form_content_disposition
from . import router


@router.post('/zone/{zone}/asset')
async def asset_upload(zone: str, request: Request):
    form = await request.form()
    response = list()
    DATA_DIR.joinpath(f'asset/{zone}').mkdir(exist_ok=True)
    for k, file in form.items():
        if not isinstance(file, StarletteUploadFile):
            continue
        path = DATA_DIR.joinpath(f'asset/{zone}/{file.filename}')
        async with aiofiles.open(path, 'wb') as fp:
            await fp.write(await file.read())
        name = paras_form_content_disposition(file.headers['content-disposition'])['name']
        storage = {'type': 'systemFile', 'info': {'path': str(path), 'size': file.size}}
        sql = sa.select(material.c.id).where(material.c.zone == zone, material.c.name == name)
        data = await database.fetch_one(sql)
        current_time = int(time.time() * 1000)
        if data:
            record = {
                'filename': file.filename,
                'storage': storage,
                'save_time': current_time,
                'update_time': current_time,
                'is_delete': True
            }
            sql = sa.update(material).where(material.c.id == data.id).values()
            await database.execute(sa.insert(material).values(record))
        else:
            record = {
                'name': name,
                'filename': file.filename,
                'ft': file.filename.rsplit('.', 1),
                'bt': 'pretreatment',
                'zone': zone,
                'storage': storage,
                'save_time': current_time,
                'expire_time': ASSET_EXPIRE_TIME,
                'create_time': current_time,
                'is_delete': False,
            }
            await database.execute(sa.insert(material).values(record))
        response.append({'name': name, 'size': storage['info']['size']})
    return JSONResponse(response)


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
    return JSONResponse(response)


@router.post('/zone/{zone}/synth/oneshot')
async def synth_oneshot(zone: str, request: Request):
    form = await request.form()
    rules = None
    for k, v in form.items():
        if k == 'rules':
            rules = v
















