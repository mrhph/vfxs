#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import typing
from pathlib import Path

import vfx4py

from vfxs.config import DATA_DIR
from .base import VFXBase

__all__ = [
    'VFXFrameFreeze',
    'VFXSlowMotion',
    'VFXViewfinderSlowAction',
    'VFXRGBShake',
    'VFXEnlargeFaces',
    'VFXPassersbyBlurred',
    'VFXPersonFollowFocus',
    'VFXMVCover',
    'concat_videos',
    'add_music_to_video',
    'convert_video'
]


VFX_RES_DIR = DATA_DIR.joinpath('vfx_res')


class VFXFrameFreeze(VFXBase):
    model = vfx4py.VFXFrameFreeze(
        str(VFX_RES_DIR.joinpath(f'VFXFrameFreeze/dgphotofrm.png')),
        str(VFX_RES_DIR.joinpath(f'VFXFrameFreeze/dgphotofrmmask.jpg')),
        0.8
    )

    def __init__(self, ori: typing.Union[Path, str], out: typing.Union[Path, str]):
        super().__init__(ori, out)
        self.vfx_code = 'VFXFrameFreeze'
        self.vfx_name = '画框定格'

    def supplied_params(self, **kwargs):
        params = [('begin_sec', int)]
        self.check_params(params, kwargs)
        return {
            'begin_sec': kwargs['begin_sec']
        }

    def dispose_of(self, begin_sec: int, *args, **kwargs):
        self.model.handle_video(self.ori, self.out, begin_sec)


class VFXSlowMotion(VFXBase):
    model = vfx4py.VFXSlowMotion()

    def __init__(self, ori: typing.Union[Path, str], out: typing.Union[Path, str]):
        super().__init__(ori, out)
        self.code = 'VFXSlowMotion'
        self.name = '慢动作'

    def supplied_params(self, **kwargs):
        params = [('begin_sec', int)]
        self.check_params(params, kwargs)
        return {
            'begin_sec': kwargs['begin_sec']
        }

    def dispose_of(self, begin_sec: int, *args, **kwargs):
        self.model.handle_video(self.ori, self.out, begin_sec)


class VFXRGBShake(VFXBase):
    model = vfx4py.VFXRGBShake(0.1, 0.2, 0.3, 15)

    def __init__(self, ori: typing.Union[Path, str], out: typing.Union[Path, str]):
        super().__init__(ori, out)
        self.vfx_code = 'VFXRGBShake'
        self.vfx_name = 'RGB震动'

    def supplied_params(self, **kwargs) -> dict:
        params = [('begin_sec', int)]
        self.check_params(params, kwargs)
        return {
            'begin_sec': kwargs['begin_sec'],
        }

    def dispose_of(self, begin_sec: int, *args, **kwargs):
        self.model.handle_video(self.ori, self.out, begin_sec)


class VFXViewfinderSlowAction(VFXBase):

    model = vfx4py.VFXViewfinderSlowAction(
        str(VFX_RES_DIR.joinpath('VFXWithModel/FaceDetect.wts')),
        str(VFX_RES_DIR.joinpath('VFXWithModel/FaceRecognition.wts')),
        1.005
    )

    def __init__(self, ori: typing.Union[Path, str], out: typing.Union[Path, str]):
        super().__init__(ori, out)
        self.code = 'VFXViewfinderSlowAction'
        self.name = '取景框慢动作'

    def supplied_params(self, **kwargs):
        params = [('begin_sec', int), ('main_char', str)]
        self.check_params(params, kwargs)
        return {
            'begin_sec': kwargs['begin_sec'],
            'main_char': kwargs['main_char']
        }

    def dispose_of(self, main_char: str, begin_sec: int, *args, **kwargs):
        viewfinder_video_path = str(VFX_RES_DIR.joinpath(f'{self.code}/viewfinder.mp4'))
        cosine_similar_thresh = 0.2
        self.model.handle_video(self.ori, viewfinder_video_path, self.out, main_char, begin_sec, cosine_similar_thresh)


class VFXWithModel(VFXBase):
    """VFXEnlargeFaces, VFXPassersbyBlurred, VFXPersonFollowFocus基类"""
    model = None

    def __init__(self, ori: typing.Union[Path, str], out: typing.Union[Path, str]):
        super().__init__(ori, out)
        self.cosine_similar_thresh = None

    def supplied_params(self, **kwargs) -> dict:
        # str
        params = [('main_char', str)]
        self.check_params(params, kwargs)
        return {
            'main_char': kwargs['main_char']
        }

    def dispose_of(self, main_char: str, *args, **kwargs):
        self.model.handle_video(self.ori, self.out, main_char, self.cosine_similar_thresh)


class VFXEnlargeFaces(VFXWithModel):

    model = vfx4py.VFXEnlargeFaces(
        str(VFX_RES_DIR.joinpath('VFXWithModel/FaceDetect.wts')),
        str(VFX_RES_DIR.joinpath('VFXWithModel/FaceRecognition.wts')),
        1.005
    )

    def __init__(self, ori: typing.Union[Path, str], out: typing.Union[Path, str]):
        super().__init__(ori, out)
        self.code = 'VFXEnlargeFaces'
        self.name = 'C位放大镜'
        self.cosine_similar_thresh = 0.2


class VFXPassersbyBlurred(VFXWithModel):

    model = vfx4py.VFXPassersbyBlurred(
        str(VFX_RES_DIR.joinpath('VFXWithModel/FaceDetect.wts')),
        str(VFX_RES_DIR.joinpath('VFXWithModel/FaceRecognition.wts')),
        1.1
    )

    def __init__(self, ori: typing.Union[Path, str], out: typing.Union[Path, str]):
        super().__init__(ori, out)
        self.code = 'VFXPassersbyBlurred'
        self.name = '路人虚化'
        self.cosine_similar_thresh = 0.2


class VFXPersonFollowFocus(VFXWithModel):

    model = vfx4py.VFXPersonFollowFocus(
        str(VFX_RES_DIR.joinpath('VFXWithModel/FaceDetect.wts')),
        str(VFX_RES_DIR.joinpath('VFXWithModel/FaceRecognition.wts')),
        1.005
    )

    def __init__(self, ori: typing.Union[Path, str], out: typing.Union[Path, str]):
        super().__init__(ori, out)
        self.code = 'VFXPersonFollowFocus'
        self.name = '变焦'
        self.cosine_similar_thresh = 0.2


class VFXMVCover(VFXBase):
    model = vfx4py.VFXMVCover(
        str(VFX_RES_DIR.joinpath(f'VFXMVCover/MVCover.png')),
        str(VFX_RES_DIR.joinpath(f'VFXMVCover/MVCover_mask.jpg')),
        0.7
    )

    def __init__(self, ori: typing.Union[Path, str], out: typing.Union[Path, str]):
        super().__init__(ori, out)
        self.vfx_code = 'VFXMVCover'
        self.vfx_name = 'MV封面'

    def supplied_params(self, **kwargs) -> dict:
        params = [('main_char', str)]
        self.check_params(params, kwargs)
        return {
            'begin_sec': kwargs['begin_sec']
        }

    def dispose_of(self, begin_sec: int, *args, **kwargs):
        self.model.handle_video(self.ori, self.out, begin_sec)


def convert_video(src: str, dst: str):
    vfx4py.convert_video(src, dst)


def concat_videos(out_path: str, *videos):
    vfx4py.concat_videos(videos, out_path)


def add_music_to_video(out_path: str, video_path: str, music_path: str):
    vfx4py.add_music_to_video(video_path, music_path, out_path)

