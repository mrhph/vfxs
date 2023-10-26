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
    'concat_videos',
    'add_music_to_video'
]


VFX_RES_DIR = DATA_DIR.joinpath('vfx_res')


class VFXFrameFreeze(VFXBase):
    def __init__(self, original: typing.Union[Path, str], output: typing.Union[Path, str]):
        super().__init__(original, output)
        self.vfx_code = 'VFXFrameFreeze'
        self.vfx_name = '画框定格'

    def supplied_params(self, **kwargs):
        # int
        params = ['begin_sec']
        self.check_params(params, kwargs)
        return {
            'photo_frm': str(VFX_RES_DIR.joinpath(f'{self.vfx_code}/dgphotofrm.png')),
            'photo_frm_mask': str(VFX_RES_DIR.joinpath(f'{self.vfx_code}/dgphotofrmmask.jpg')),
            'begin_sec': kwargs['begin_sec'],
            'scale': 0.8
        }

    def dispose_of(self, photo_frm: str, photo_frm_mask: str, begin_sec: int, scale: float, *args, **kwargs):
        skip_rate = 1
        model = vfx4py.VFXFrameFreeze(photo_frm, photo_frm_mask, scale)
        model.handle_video(self.input, self.output, begin_sec, skip_rate)


class VFXSlowMotion(VFXBase):
    def __init__(self, original: typing.Union[Path, str], output: typing.Union[Path, str]):
        super().__init__(original, output)
        self.vfx_code = 'VFXSlowMotion'
        self.vfx_name = '慢动作'

    def supplied_params(self, **kwargs):
        params = ['begin_sec', 'end_sec']
        self.check_params(params, kwargs)
        return {'begin_sec': kwargs['begin_sec'], 'end_sec': kwargs['end_sec']}

    def dispose_of(self, begin_sec: int, end_sec: int, *args, **kwargs):
        model = vfx4py.VFXSlowMotion()
        model.handle_video(self.input, self.output, begin_sec, end_sec)


class VFXViewfinderSlowAction(VFXBase):
    def __init__(self, original: typing.Union[Path, str], output: typing.Union[Path, str]):
        super().__init__(original, output)
        self.vfx_code = 'VFXViewfinderSlowAction'
        self.vfx_name = '取景框慢动作'

    def supplied_params(self, **kwargs):
        # int, int
        params = ['begin_sec', 'end_sec']
        self.check_params(params, kwargs)
        return {
            'viewfinder_video_path': str(VFX_RES_DIR.joinpath(f'{self.vfx_code}/viewfinder.mp4')),
            'begin_sec': kwargs['begin_sec'],
            'end_sec': kwargs['end_sec'],
        }

    def dispose_of(self, viewfinder_video_path: str, begin_sec: int, end_sec: int, *args, **kwargs):
        model = vfx4py.VFXViewfinderSlowAction()
        model.handle_video(self.input, viewfinder_video_path, self.output, begin_sec, end_sec)


class VFXRGBShake(VFXBase):
    def __init__(self, original: typing.Union[Path, str], output: typing.Union[Path, str]):
        super().__init__(original, output)
        self.vfx_code = 'VFXRGBShake'
        self.vfx_name = 'RGB震动'

    def supplied_params(self, **kwargs) -> dict:
        # int, int, list[float], int
        params = ['begin_sec', 'end_sec', 'max_magnifications', 'shake_time']
        self.check_params(params, kwargs)
        return {
            'begin_sec': kwargs['begin_sec'],
            'end_sec': kwargs['end_sec'],
            'max_magnifications': kwargs['max_magnifications'],
            'shake_time': kwargs['shake_time']
        }

    def dispose_of(
            self,
            max_magnifications: list[float], shake_time: int, begin_sec: int, end_sec: int,
            *args, **kwargs
    ):
        model = vfx4py.VFXRGBShake(max_magnifications[0], max_magnifications[1], max_magnifications[2], shake_time)
        model.handle_video(self.input, self.output, begin_sec, end_sec)


class VFXWithModel(VFXBase):
    """VFXEnlargeFaces, VFXPassersbyBlurred, VFXPersonFollowFocus基类"""
    def __init__(self, original: typing.Union[Path, str], output: typing.Union[Path, str]):
        super().__init__(original, output)
        self.model_cls: typing.Optional[typing.ClassVar] = None
        self.scale: typing.Optional[float] = None

    def supplied_params(self, **kwargs) -> dict:
        # str, float, float, str
        params = ['main_char', 'scale', 'cosine_similar_thresh']
        self.check_params(params, kwargs)
        return {
            'fd_model': str(VFX_RES_DIR.joinpath('VFXWithModel/FaceDetect.wts')),       # 人脸检测模型路径
            'fr_model': str(VFX_RES_DIR.joinpath('VFXWithModel/FaceRecognition.wts')),  # 人脸识别模型路径
            'scale': self.scale,
            'cosine_similar_thresh': kwargs['cosine_similar_thresh'],
            'main_char': kwargs['main_char']   # 主角人脸图片
        }

    def dispose_of(
            self,
            fd_model: str, fr_model: str, main_char: str, scale: float, cosine_similar_thresh: float,
            *args, **kwargs
    ):
        model = self.model_cls(fd_model, fr_model, scale, cosine_similar_thresh)
        model.handle_video(self.input, self.output, main_char)


class VFXEnlargeFaces(VFXWithModel):
    def __init__(self, original: typing.Union[Path, str], output: typing.Union[Path, str]):
        super().__init__(original, output)
        self.vfx_code = 'VFXEnlargeFaces'
        self.vfx_name = 'C位放大镜'
        self.model_cls = vfx4py.VFXEnlargeFaces
        self.scale = 1.005


class VFXPassersbyBlurred(VFXWithModel):
    def __init__(self, original: typing.Union[Path, str], output: typing.Union[Path, str]):
        super().__init__(original, output)
        self.vfx_code = 'VFXPassersbyBlurred'
        self.vfx_name = '路人虚化'
        self.model_cls = vfx4py.VFXPassersbyBlurred
        self.scale = 1.1


class VFXPersonFollowFocus(VFXWithModel):
    def __init__(self, original: typing.Union[Path, str], output: typing.Union[Path, str]):
        super().__init__(original, output)
        self.vfx_code = 'VFXPersonFollowFocus'
        self.vfx_name = '变焦'
        self.model_cls = vfx4py.VFXPersonFollowFocus
        self.scale = 1.005


class VFXMVCover(VFXBase):
    def __init__(self, original: typing.Union[Path, str], output: typing.Union[Path, str]):
        super().__init__(original, output)
        self.vfx_code = 'VFXMVCover'
        self.vfx_name = 'MV封面'

    def supplied_params(self, **kwargs) -> dict:
        # int, float
        params = ['begin_sec']
        self.check_params(params, kwargs)
        return {
            'cover_path': str(VFX_RES_DIR.joinpath(f'{self.vfx_code}/MVCover.png')),
            'cover_mask_path': str(VFX_RES_DIR.joinpath(f'{self.vfx_code}/MVCover_mask.jpg')),
            'scale': 0.7,
            'begin_sec': kwargs['begin_sec']
        }

    def dispose_of(
            self,
            cover_path: str, cover_mask_path: str, scale: float, begin_sec: int,
            *args, **kwargs
    ):
        model = vfx4py.VFXMVCover(cover_path, cover_mask_path, scale)
        model.handle_video(self.input, self.output, begin_sec)


def concat_videos(out_path: str, *videos):
    vfx4py.concat_videos(videos, out_path)


def add_music_to_video(out_path: str, video_path: str, music_path: str):
    vfx4py.add_music_to_video(video_path, music_path, out_path)

