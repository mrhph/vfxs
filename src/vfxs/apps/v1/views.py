#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import json
import time
import uuid

import aiofiles
import sqlalchemy as sa
from fastapi import Request
from starlette.datastructures import UploadFile as StarletteUploadFile

from vfxs.config import ASSET_EXPIRE_TIME, DATA_DIR
from vfxs.models import database, material
from vfxs.utils.request import paras_form_content_disposition
from vfxs.utils.response import jsonify, error_jsonify
from vfxs.vfx import get_vfx_handle
from . import router


ASSET_DIR = DATA_DIR.joinpath('asset')
VFX_OUT_DIR = DATA_DIR.joinpath('vfx_out')
ASSET_DIR.mkdir(parents=True, exist_ok=True)
VFX_OUT_DIR.mkdir(parents=True, exist_ok=True)


async def save_or_update_zone_asset(zone: str, file: StarletteUploadFile) -> (str, dict):
    ft = file.filename.rsplit('.', 1)[-1]  # 文件类型
    name = paras_form_content_disposition(file.headers['content-disposition'])['name']  # name
    ASSET_DIR.joinpath(zone).mkdir(parents=True, exist_ok=True)
    path = ASSET_DIR.joinpath(f'{zone}/{name}.{ft}')
    async with aiofiles.open(path, 'wb') as fp:
        await fp.write(await file.read())
    storage = {
        'type': 'systemFile',
        'info': {'path': str(path), 'size': file.size, 'ft': ft}
    }
    sql = sa.select(material.c.id).where(material.c.zone == zone, material.c.name == name)
    data = await database.fetch_one(sql)
    current_time = int(time.time() * 1000)
    if data:
        record = {
            'filename': file.filename,
            'storage': storage,
            'save_time': current_time,
            'update_time': current_time,
            'is_delete': False
        }
        sql = sa.update(material).where(material.c.id == data.id).values(record)
        await database.execute(sql)
    else:
        record = {
            'name': name,
            'filename': file.filename,
            'ft': file.filename.rsplit('.', 1)[-1],
            'bt': 'pretreatment',
            'zone': zone,
            'storage': storage,
            'save_time': current_time,
            'create_time': current_time,
            'update_time': current_time,
            'expire_time': ASSET_EXPIRE_TIME,
            'is_delete': False,
        }
        await database.execute(sa.insert(material).values(record))
    return name, storage


@router.post('/zone/{zone}/asset')
async def asset_upload(zone: str, request: Request):
    form = await request.form()
    response = list()
    for k, file in form.items():
        if not isinstance(file, StarletteUploadFile):
            continue
        name, storage = await save_or_update_zone_asset(zone, file)
        response.append({'name': name, 'size': storage['info']['size']})
    return jsonify(response)


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
    return jsonify(response)


@router.post('/zone/{zone}/synth/oneshot')
async def synth_oneshot(zone: str, request: Request):
    form = await request.form()
    rules = dict()
    for k, v in form.items():
        if k == 'rules':
            rules = json.loads(v)
        if isinstance(v, StarletteUploadFile):
            await save_or_update_zone_asset(zone, v)
    if not rules:
        return error_jsonify(message='缺少合成规则参数rules')
    response = list()
    for clips in rules['clips']:
        sql = sa.select(material.c.storage).where(
            material.c.zone == zone, material.c.name == clips['name']
        )
        data = await database.fetch_one(sql)
        original = data.storage['info']['path']
        name = uuid.uuid4().hex
        out = VFX_OUT_DIR.joinpath('%s.%s' % (name, data.storage['info']['ft']))
        handle = get_vfx_handle(clips['vfx']['code'])(original, out)
        handle(**clips['vfx']['params'])
        response.append(name)
    return jsonify(response)
