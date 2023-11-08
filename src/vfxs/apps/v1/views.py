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

from vfxs.config import TMP_DIR, MATERIAL_DIR
from vfxs.models import database, material
from vfxs.utils.cos import CosStorage
from vfxs.utils.logger import LOGGER
from vfxs.utils.request import paras_form_content_disposition
from vfxs.utils.response import response_200, response_400
from vfxs.vfx import get_vfx_handle, concat_videos, add_music_to_video, convert_video
from . import router


@router.post('/zone/{zone}/asset')
async def asset_upload(zone: str, request: Request):
    form = await request.form()
    response = list()
    MATERIAL_DIR.joinpath(zone).mkdir(parents=True, exist_ok=True)
    for k, file in form.items():
        if not isinstance(file, StarletteUploadFile):
            continue
        ft = file.filename.rsplit('.', 1)[-1]  # 文件类型
        name = paras_form_content_disposition(file.headers['content-disposition'])['name']  # name

        if ft == 'acc':  # 音频数据
            bt = 'bgm'
            path = MATERIAL_DIR.joinpath(f'{zone}/{name}.mp4')
            async with aiofiles.open(path, 'wb') as fp:
                await fp.write(await file.read())
        else:            # 视频数据需要做格式对齐
            ft, bt = 'mp4', 'transition'
            tmp = TMP_DIR.joinpath(f'{uuid.uuid4().hex}.{ft}')
            path = MATERIAL_DIR.joinpath(f'{zone}/{name}.mp4')
            async with aiofiles.open(tmp, 'wb') as fp:
                await fp.write(await file.read())
            convert_video(str(tmp), str(path))
            tmp.unlink(missing_ok=True)
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
                'expire_time': 0,
                'is_delete': False
            }
            sql = sa.update(material).where(material.c.id == data.id).values(record)
            await database.execute(sql)
        else:
            record = {
                'name': name,
                'filename': file.filename,
                'ft': file.filename.rsplit('.', 1)[-1],
                'bt': bt,
                'zone': zone,
                'storage': storage,
                'save_time': current_time,
                'create_time': current_time,
                'update_time': current_time,
                'expire_time': 0,
                'is_delete': False,
            }
            await database.execute(sa.insert(material).values(record))
        LOGGER.info(f'保存素材{name}. {path}')
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


@router.post('/zone/{zone}/synth/oneshot')
async def synth_oneshot(zone: str, request: Request):
    form = await request.form()
    rules, binary_files = dict(), dict()
    # 提取合成规则及二进制数据，数据存入tmp下
    for k, item in form.items():
        if k == 'rules':
            rules = json.loads(item)
        if isinstance(item, StarletteUploadFile):
            filename = item.filename
            name = paras_form_content_disposition(item.headers['content-disposition'])['name']  # name
            path = TMP_DIR.joinpath(filename)
            async with aiofiles.open(path, 'wb') as f:
                await f.write(await item.read())
            binary_files[name] = path
    if not rules:
        return response_400(message='缺少合成规则参数rules')

    # 提取人物视频及需要进行特效处理的人物视频
    videos, use_vfx_videos = list(), list()
    for clip in rules['clips']:
        name = clip['name']
        path = binary_files.get(name) if 'vfx' in clip else await material.get_storage_path(zone, name)
        if clip.get('vfx'):
            use_vfx_videos.append((name, path, clip['vfx']))
        if not path:
            return response_400(f'{name}在素材库或者form-data中不存在，请检查入参')
        videos.append((name, path))

    # 进行特效处理
    vfx_videos = dict()
    for name, path, effect in use_vfx_videos:
        if effect['code'] in ['VFXEnlargeFaces', 'VFXPassersbyBlurred', 'VFXPersonFollowFocus']:
            effect['params']['main_char'] = str(binary_files[effect['params']['main_char']])
        _out = TMP_DIR.joinpath(f'{uuid.uuid4().hex}.mp4')
        handle = get_vfx_handle(effect['code'])(path, _out)
        handle(**effect['params'])
        vfx_videos[name] = _out

    # 替换需要进行特效处理的人物视频，顺序不能乱
    videos = [str(vfx_videos.get(name, path)) for name, path in videos]
    # 视频合并
    if len(videos) == 1:
        video = videos[0]
    else:
        video = TMP_DIR.joinpath(f'{uuid.uuid4().hex}.mp4')
        concat_videos(str(video), *videos)
    # 添加音乐
    if rules.get('music'):
        music = await material.get_storage_path(zone, rules['music']['name'])
        result = TMP_DIR.joinpath(f'{uuid.uuid4().hex}.mp4')
        add_music_to_video(str(result), video, music)
    else:
        result = video
    # 上传至cos
    upload_ret = CosStorage.upload_file(str(result), result.name)
    response = {
        'cos': {'Bucket': upload_ret.Bucket, 'Key': upload_ret.Key, 'Location': upload_ret.Location},
        'path': str(result)
    }
    return response_200(response)
