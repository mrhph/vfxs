#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import abc
import os
import typing

from pathlib import Path


class VFXBase:
    def __init__(self, original: typing.Union[Path, str], output: typing.Union[Path, str]):

        if not os.path.exists(original):
            raise FileNotFoundError(f'待处理文件{original}不存在')

        self.input = str(original)
        self.output = str(output)
        self.vfx_code: str = ...
        self.vfx_name: str = ...
        self.model = None

    def export_cos(self):
        pass

    def check_params(self, params: list[str], kw: dict):
        diff = set(params) - set(kw.keys())
        if diff:
            raise ValueError(f'{self.vfx_name}中缺少{list(diff)}入参')

    @abc.abstractmethod
    def supplied_params(self, **kwargs) -> dict:
        raise NotImplementedError

    @abc.abstractmethod
    def dispose_of(self, *args, **kwargs):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        self.dispose_of(**self.supplied_params(**kwargs))
        self.export_cos()
