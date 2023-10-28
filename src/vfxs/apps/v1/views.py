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

from vfxs.config import ASSET_EXPIRE_TIME, DATA_DIR, COS_BUCKET_NAME
from vfxs.models import database, material
from vfxs.utils.request import paras_form_content_disposition
from vfxs.utils.response import response_200, response_400
from vfxs.utils.cos import CosStorage
from vfxs.vfx import get_vfx_handle, concat_videos, add_music_to_video
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
            'expire_time': current_time + ASSET_EXPIRE_TIME,
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
            'expire_time': current_time + ASSET_EXPIRE_TIME,
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
    return response_200(response)


@router.get('/zone/{zone}/asset')
async def get_asset(zone: str, bt: str = 'pretreatment'):
    if bt != 'pretreatment':
        return response_400(message=f'暂不支持非{bt}类型文件查询')
    sql = sa.select(
        material.c.name, material.c.storage
    ).where(material.c.zone == zone, material.c.bt == bt)
    data = await database.fetch_all(sql)
    response = [{'name': i.name, 'size': i.storage['info']['size']} for i in data]
    return response_200(response)


async def get_storage_path(zone: str, name: str) -> str:
    sql = sa.select(material.c.storage).where(
        material.c.zone == zone, material.c.name == name
    )
    data = await database.fetch_one(sql)
    return data.storage['info']['path']


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
        return response_400(message='缺少合成规则参数rules')
    videos = list()
    for clip in rules['clips']:
        if clip['vfx']['code'] in ['VFXEnlargeFaces', 'VFXPassersbyBlurred', 'VFXPersonFollowFocus']:
            clip['vfx']['params']['main_char'] = await get_storage_path(zone, clip['vfx']['params']['main_char'])
        ori_path = await get_storage_path(zone, clip['name'])
        out_path = VFX_OUT_DIR.joinpath(f'{uuid.uuid4().hex}.mp4')
        handle = get_vfx_handle(clip['vfx']['code'])(ori_path, out_path)
        handle(**clip['vfx']['params'])
        videos.append(str(out_path))
    if len(videos) == 1:
        video = videos[0]
    else:
        video = str(VFX_OUT_DIR.joinpath(f'{uuid.uuid4().hex}.mp4'))
        concat_videos(video, *videos)
    if rules.get('music'):
        music = await get_storage_path(zone, rules['music']['name'])
        result = str(VFX_OUT_DIR.joinpath(f'{uuid.uuid4().hex}.mp4'))
        add_music_to_video(result, video, music)
    else:
        result = video

    cos_key = uuid.uuid4().hex + '.mp4'
    CosStorage.upload_file(result, cos_key)

    response = {
        'cos': {'bucket': COS_BUCKET_NAME, 'key': cos_key},
        'path': result
    }
    return response_200(response)
