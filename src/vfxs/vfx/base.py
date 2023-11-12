#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import abc
import os
import typing

from pathlib import Path


class VFXBase:
    def __init__(self, ori: typing.Union[Path, str], out: typing.Union[Path, str]):

        if not os.path.exists(ori):
            raise FileNotFoundError(f'待处理文件{ori}不存在')

        self.ori: str = str(ori)
        self.out: str = str(out)
        self.code: str = ...
        self.name: str = ...

    def check_params(self, params: list[tuple[str, type]], kw: dict):
        for i in params:
            if i not in kw:
                raise ValueError(f'{self.name}参数{i[0]}缺失')
            if not isinstance(kw[i[0]], i[1]):
                raise ValueError(f'{self.name}参数{i[0]}类型错误, 应为{i[1].__name__}')

    @abc.abstractmethod
    def supplied_params(self, **kwargs) -> dict:
        raise NotImplementedError

    @abc.abstractmethod
    def dispose_of(self, *args, **kwargs):
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        self.dispose_of(**self.supplied_params(**kwargs))
