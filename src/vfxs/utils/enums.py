#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import enum


class ResponseCode(enum.IntEnum):
    E0 = 0
    E10000 = 10000  # 参数错误
    E10001 = 10001  # 合成失败
    E10002 = 10002  # 任务提交失败
    E10003 = 10003  # 文件找不到
    E10100 = 10100  # 内部错误


if __name__ == '__main__':
    print(ResponseCode)
    print('E10000' in ResponseCode)
