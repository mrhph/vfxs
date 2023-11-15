#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import os
import asyncio
import json
import pathlib
import time
import typing
import uuid
from concurrent.futures import ProcessPoolExecutor

import aiofiles
import sqlalchemy as sa
from fastapi import Request
from starlette.datastructures import UploadFile as StarletteUploadFile

from vfxs.config import TMP_DIR, MATERIAL_DIR
from vfxs.models import database, material
from vfxs.utils.cos import CosStorage
from vfxs.utils.logger import LOGGER
from vfxs.utils.request import paras_form_content_disposition
from vfxs.utils.response import response_200, response_400, response_500
from vfxs.vfx import convert_video, get_vfx_handle, concat_videos, add_music_to_video
from . import router

MAIN_CHAR_VFX = ['VFXViewfinderSlowAction', 'VFXEnlargeFaces', 'VFXPassersbyBlurred', 'VFXPersonFollowFocus']


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
        if ft == 'aac':  # 音频数据
            bt = 'bgm'
            path = MATERIAL_DIR.joinpath(f'{zone}/{name}.{ft}')
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


def handle_video(idx: int, ori: typing.Union[pathlib.Path, str], effects: list[dict], video_name: str):
    out = None
    LOGGER.info(f'处理{video_name}视频, 参数: {effects}')
    for effect in effects:
        out = TMP_DIR.joinpath(f'{uuid.uuid4().hex}.mp4')
        handle = get_vfx_handle(effect['code'])(ori, out)
        try:
            handle(**effect['params'])
        except Exception as e:
            LOGGER.error(f'{handle.name}处理{video_name}失败. 原因: {e}')
            out = ori
        else:
            ori = out
    return idx, out


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

    LOGGER.info(rules)

    # 提取人物视频及需要进行特效处理的人物视频
    videos, use_vfx_videos = list(), list()
    for idx, clip in enumerate(rules['clips']):
        name = clip['name']
        path = binary_files.get(name) if 'vfx' in clip else await material.get_storage_path(zone, name)
        if clip.get('vfx'):
            use_vfx_videos.append((idx, name, path, clip['vfx']))
        if not path:
            return response_400(f'{name}在素材库或者form-data中不存在，请检查入参')
        videos.append((idx, name, path, clip.get('vfx', None)))

    # 进行特效处理
    vfx_videos = dict()
    if use_vfx_videos:
        with ProcessPoolExecutor(max_workers=len(use_vfx_videos)) as pool:
            loop = asyncio.get_event_loop()
            tasks = list()
            for idx, name, path, effects in use_vfx_videos:
                for effect in effects:  # 处理人像图片为具体路径
                    if effect['code'] in MAIN_CHAR_VFX:
                        effect['params']['main_char'] = str(binary_files[effect['params']['main_char']])
                tasks.append(loop.run_in_executor(pool, handle_video, idx, path, effects, name))
            try:
                result = await asyncio.gather(*tasks)
            except Exception as e:
                return response_500(message=str(e))
            vfx_videos = {i[0]: i[1] for i in result}
            
    # CU: 做个视频是否正常生成的检查 以防视频拼接出错
    for idx, save_video_path in vfx_videos.items():
        is_exists = os.path.exists(save_video_path)
        if not is_exists:
            LOGGER.error(f"特效{videos[idx][1]}生成的视频{save_video_path}不存在, 将替换为原视频")
            vfx_videos[idx] = videos[idx][2]
            
    # 替换需要进行特效处理的人物视频，顺序不能乱
    videos = [str(vfx_videos[idx] if effect else path) for idx, name, path, effect in videos]

    # 视频合并
    if len(videos) == 1:
        video = pathlib.Path(videos[0])
    else:
        video = TMP_DIR.joinpath(f'{uuid.uuid4().hex}.mp4')
        concat_videos(str(video), *videos)
    # 添加音乐
    if rules.get('music'):
        music = await material.get_storage_path(zone, rules['music']['name'])
        result = TMP_DIR.joinpath(f'{uuid.uuid4().hex}.mp4')
        add_music_to_video(str(result), str(video), str(music))
    else:
        result = video
    # 上传至cos
    upload_ret = CosStorage.upload_file(str(result), result.name)
    response = {
        'cos': {'Bucket': upload_ret.Bucket, 'Key': upload_ret.Key, 'Location': upload_ret.Location},
        'path': str(result)
    }
    return response_200(response)

