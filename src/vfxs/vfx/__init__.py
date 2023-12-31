#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8

from .base import VFXBase
from .vfx import *

VFX_MAP = {
    'VFXFrameFreeze': VFXFrameFreeze,
    'VFXSlowMotion': VFXSlowMotion,
    'VFXViewfinderSlowAction': VFXViewfinderSlowAction,
    'VFXRGBShake': VFXRGBShake,
    'VFXEnlargeFaces': VFXEnlargeFaces,
    'VFXPassersbyBlurred': VFXPassersbyBlurred,
    'VFXPersonFollowFocus': VFXPersonFollowFocus,
    'VFXMVCover': VFXMVCover
}


def get_vfx_handle(code: str) -> VFXBase:
    if code not in VFX_MAP:
        raise KeyError(f'{code}特效不存在')
    return VFX_MAP[code]
