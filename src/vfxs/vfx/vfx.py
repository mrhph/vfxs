#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import typing
from pathlib import Path

import vfx4py

from .base import VFXBase


class VFXSlowMotion(VFXBase):
    def __init__(self, original: typing.Union[Path, str], output: typing.Union[Path, str]):
        super().__init__(original, output)
        self.vfx_code = 'VFXSlowMotion'
        self.vfx_name = '视频慢放'

    def supplied_params(self, **kwargs):
        params = ['start_time', 'end_time']
        self.check_params(params, kwargs)
        return {'start_time': kwargs['start_time'], 'end_time': kwargs['end_time']}

    def dispose_of(self, start_time: int, end_time: int, *args, **kwargs):
        model = vfx4py.VFXSlowMotion()
        model.slow_motion(self.input, self.output, start_time, end_time)


class VFXFrameFreeze(VFXBase):
    def __init__(self, original: typing.Union[Path, str], output: typing.Union[Path, str]):
        super().__init__(original, output)
        self.vfx_code = 'VFXFrameFreeze'
        self.vfx_name = '画框定格'
        self.model = vfx4py.VFXFrameFreeze()

    def supplied_params(self, **kwargs):
        params = ['photo_frm', 'photo_frm_mask', 'begin_sec']
        self.check_params(params, kwargs)
        return {
            'photo_frm': kwargs['photo_frm'],
            'photo_frm_mask': kwargs['photo_frm_mask'],
            'begin_sec': kwargs['begin_sec'],
            'scale': kwargs.get('scale', 0.8)
        }

    def dispose_of(self, photo_frm: str, photo_frm_mask: str, begin_sec: int, scale=0.8, *args, **kwargs):
        skip_rate = 1
        model = vfx4py.VFXFrameFreeze(photo_frm, photo_frm_mask, scale)
        model.frame_freeze(self.input, self.output, begin_sec, skip_rate)


class VFXEnlargeFaces:
    pass
