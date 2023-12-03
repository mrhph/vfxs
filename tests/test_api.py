#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import json
import requests


# HOST = 'http://118.195.171.96:8888'
HOST = 'http://127.0.0.1:8000'


def test_asset_upload():
    url = f"{HOST}/v1.0/zone/aaa/asset"
    payload = {'rules': json.dumps({'a': 123})}
    files = [
        (
            '测试',
            (
                '测试.mp4',
                open('./data/测试.mp4', 'rb'),
                'application/octet-stream',
            )
        ),
        (
            'test',
            (
                'test_1.mp4',
                open('./data/test_1.mp4', 'rb'),
                'application/octet-stream',
            )
        )
    ]
    headers = {}
    response = requests.post(url, headers=headers, files=files, data=payload)
    print(response.status_code)
    print(response.text)


def test_asset_list():
    url = f"{HOST}/v1.0/zone/aaa/asset"
    response = requests.get(url)
    print(response.json())


def synth_oneshot(rules):
    url = f"{HOST}/v1.0/zone/aaa/synth/oneshot"
    payload = {'rules': json.dumps(rules)}
    files = [
        (
            'test_1',
            (
                'test_1.mp4',
                open('./data/test_1.mp4', 'rb'),
                'application/octet-stream',
            )
        ),
        (
            'mainchar',
            (
                'mainchar.jpg',
                open('./data/mainchar.jpg', 'rb'),
                'application/octet-stream',
            )
        )
    ]
    headers = {}
    response = requests.post(url, headers=headers, data=payload, files=files)
    print(response.text)


def test_frame_freeze():
    """画框定格"""
    rules = {
        "clips": [
            {
                "name": "test_1",
                "vfx": {
                    "code": "VFXFrameFreeze",
                    "params": {"begin_sec": 1}
                }
            }
        ]
    }
    synth_oneshot(rules)


def test_slow_motion():
    """慢动作"""
    rules = {
        "clips": [
            {
                "name": "test_1",
                "vfx": {
                    "code": "VFXSlowMotion",
                    "params": {"begin_sec": 1, "end_sec": 5}
                }
            }
        ]
    }
    synth_oneshot(rules)


def test_viewfinder_slow_action():
    """取景框慢动作"""
    rules = {
        "clips": [
            {
                "name": "test_1",
                "vfx": {
                    "code": "VFXViewfinderSlowAction",
                    "params": {"begin_sec": 1, "end_sec": 5}
                }
            },
        ]
    }
    synth_oneshot(rules)


def test_rgb_shake():
    """RGB震动"""
    rules = {
        "clips": [
            {
                "name": "test_1",
                "vfx": {
                    "code": "VFXRGBShake",
                    "params": {"begin_sec": 1, "end_sec": 5}
                }
            },
        ]
    }
    synth_oneshot(rules)


def test_xmv_cover():
    """MV封面"""
    rules = {
        "clips": [
            {
                "name": "test_1",
                "vfx": [{
                    "code": "VFXMVCover",
                    "params": {"begin_sec": 1}
                }]
            },
        ]
    }
    synth_oneshot(rules)


def test_enlarge_faces():
    """C位放大镜"""
    rules = {
        "clips": [
            {
                "name": "test_1",
                "vfx": [{
                    "code": "VFXEnlargeFaces",
                    "params": {"main_char": 'mainchar'}
                }]
            },
        ]
    }
    synth_oneshot(rules)


def test_passersby_blurred():
    """路人虚化"""
    rules = {
        "clips": [
            {
                "name": "test_1",
                "vfx": {
                    "code": "VFXPassersbyBlurred",
                    "params": {"main_char": 'mainchar'}
                }
            },
        ]
    }
    synth_oneshot(rules)


def test_person_follow_focus():
    """变焦"""
    rules = {
        "clips": [
            {
                "name": "test_1",
                "vfx": {
                    "code": "VFXPersonFollowFocus",
                    "params": {"main_char": 'mainchar'}
                }
            },
        ]
    }
    synth_oneshot(rules)


def test_all_video():
    rules = {
        "clips": [
            {
                "name": "test_1",
                "vfx": {
                    "code": "VFXFrameFreeze",
                    "params": {"begin_sec": 1}
                }
            },
            {
                "name": "test_1",
                "vfx": {
                    "code": "VFXEnlargeFaces",
                    "params": {"main_char": 'mainchar'}
                }
            },
        ]
    }
    synth_oneshot(rules)


def test_all_video_with_music():
    rules = {
        "clips": [
            {
                "name": "test_1",
                "vfx": [
                    {
                        "code": "VFXFrameFreeze",
                        "params": {"begin_sec": 1}
                    },
                    {
                        "code": "VFXEnlargeFaces",
                        "params": {"main_char": 'mainchar'}
                    }
                ]
            },
            {
                "name": "test_2"
            }
        ],
        'music': {
            "name": "bgm"
        }
    }
    synth_oneshot(rules)
