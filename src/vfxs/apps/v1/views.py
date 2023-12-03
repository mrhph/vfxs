#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import asyncio
import json
import os
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
from vfxs.utils.response import response_200, response_400, response_500
from vfxs.utils.wrapper import SyncToAsyncWrapper
from vfxs.vfx import convert_video, get_vfx_handle, concat_videos, add_music_to_video, VFX_MAP, change_video_profile
from . import router

MAIN_CHAR_VFX = ['VFXViewfinderSlowAction', 'VFXEnlargeFaces', 'VFXPassersbyBlurred', 'VFXPersonFollowFocus']


def init_all_model():
    for k, v in VFX_MAP.items():
        LOGGER.info(f'{os.getpid()}进程预加载{k}模型')
        v.init_model()


# 处理特效的进程池，需要预先加载engine模型所以会占用显存，不能设置大，一个景区一般是有3个视频片段做处理
POOL_VFX_EFFECT = ProcessPoolExecutor(max_workers=3)
# 不需要加载模型的进程池，用来处理合并、bgm等
POOL_VFX = ProcessPoolExecutor(max_workers=4)


@router.post('/zone/{zone}/asset')
async def asset_upload(zone: str, request: Request):
    form = await request.form()
    response = list()
    MATERIAL_DIR.joinpath(zone).mkdir(parents=True, exist_ok=True)
    for name, file in form.items():
        if not isinstance(file, StarletteUploadFile):
            continue
        ft = file.filename.rsplit('.', 1)[-1]  # 文件类型
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


def handle_video(key: int, ori: typing.Union[pathlib.Path, str], effects: list[dict], video_name: str):
    out = None
    LOGGER.info(f'处理{video_name}视频, 参数: {effects}')
    for idx, effect in enumerate(effects):
        t1 = (time.time() * 1000)
        LOGGER.info(f'处理{video_name}特效{effect["code"]}, params: {effect["params"]}')
        out = TMP_DIR.joinpath(f'{uuid.uuid4().hex}.mp4')
        cls = get_vfx_handle(effect['code'])
        if not getattr(cls, 'model', None):
            LOGGER.info(f'{os.getpid()}进程预加载{effect["code"]}模型')
            cls.init_model()
        handle = cls(ori, out)
        try:
            handle(**effect['params'])
        except Exception as e:
            LOGGER.error(f'{handle.name}处理{video_name}失败. 原因: {e}')
            out = ori
        else:
            ori = out
            # 多特效视频对中间视频结果进行profile设置
            if idx + 1 < len(effects):
                out = TMP_DIR.joinpath(f'{uuid.uuid4().hex}.mp4')
                change_video_profile(str(ori), str(out))
                ori = out
        LOGGER.info(f'处理{video_name}特效{effect["code"]}完成, 耗时: {(time.time() * 1000) - t1}ms')
    return key, out


@router.post('/zone/{zone}/synth/oneshot')
async def synth_oneshot(zone: str, request: Request):
    form = await request.form()
    rules, binary_files = dict(), dict()
    # 提取合成规则及二进制数据，数据存入tmp下
    for name, item in form.items():
        if name == 'rules':
            rules = json.loads(item)
        if isinstance(item, StarletteUploadFile):
            filename = item.filename
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
        loop = asyncio.get_event_loop()
        tasks = list()
        for idx, name, path, effects in use_vfx_videos:
            for effect in effects:  # 处理人像图片为具体路径
                if effect['code'] in MAIN_CHAR_VFX:
                    effect['params']['main_char'] = str(binary_files[effect['params']['main_char']])
            tasks.append(loop.run_in_executor(POOL_VFX_EFFECT, handle_video, idx, path, effects, name))
        try:
            result = await asyncio.gather(*tasks)
        except Exception as e:
            return response_500(message=str(e))
        vfx_videos = {i[0]: i[1] for i in result}
    # 替换需要进行特效处理的人物视频，顺序不能乱
    videos = [str(vfx_videos[idx] if effect else path) for idx, name, path, effect in videos]

    # 视频合并
    if len(videos) == 1:
        video = pathlib.Path(videos[0])
    else:
        video = TMP_DIR.joinpath(f'{uuid.uuid4().hex}.mp4')
        func = SyncToAsyncWrapper(concat_videos, POOL_VFX)
        await func(str(video), *videos)
        if not video.exists():
            return response_500(f'视频拼接失败, 未有结果视频生成')
        LOGGER.info(f'视频拼接完成 to {video} ')
    # 添加音乐
    if rules.get('music'):
        music = await material.get_storage_path(zone, rules['music']['name'])
        result = TMP_DIR.joinpath(f'{uuid.uuid4().hex}.mp4')
        func = SyncToAsyncWrapper(add_music_to_video, POOL_VFX)
        await func(str(video), str(music), str(result))
        if not result.exists():
            return response_500(f'音乐合成失败, 未有结果视频生成')
        LOGGER.info(f'bgm添加完成 to {result}')
    else:
        result = video
    # 上传至cos
    upload_ret = CosStorage.upload_file(str(result), result.name)
    url = CosStorage.get_object_url(result.name)
    response = {
        'cos': {'Bucket': upload_ret.Bucket, 'Key': upload_ret.Key, 'Location': url}
    }
    return response_200(response)

