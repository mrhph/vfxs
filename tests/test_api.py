#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import json
import requests


HOST = 'http://118.195.171.96:8888'
# HOST = 'http://127.0.0.1:8000'


def test_asset_upload():
    url = f"{HOST}/v1.0/zone/aaa/asset"
    payload = {'rules': json.dumps({'a': 123})}
    files = [
        (
            'a',
            (
                'a.mp4',
                open('./data/a.mp4', 'rb'),
                'application/octet-stream',
            )
        ),
        (
            'b',
            (
                'b.mp4',
                open('./data/b.mp4', 'rb'),
                'application/octet-stream',
                # {'Content-Disposition': 'form-data; name="b"; filename="b.mp4"'}
            )
        ),
    ]
    headers = {}
    response = requests.post(url, headers=headers, data=payload, files=files)
    print(response.status_code)
    print(response.text)


def test_asset_list():
    url = f"{HOST}/v1.0/zone/aaa/asset"
    response = requests.get(url)
    print(response.json())


def test_synth_oneshot():
    url = f"{HOST}/v1.0/zone/aaa/synth/oneshot"
    rules = {
        "clips": [
            {
                "name": "test_vfx1",
                "vfx": {
                    "code": "VFXSlowMotion",
                    "params": {"start_time": 1, "end_time": 5}
                }
            },
        ]
    }
    payload = {'rules': json.dumps(rules)}
    files = [
        (
            'test_vfx1',
            (
                'test_vfx1.mp4',
                open('./data/test_vfx1.mp4', 'rb'),
                'application/octet-stream',
            )
        )
    ]
    headers = {}
    response = requests.post(url, headers=headers, data=payload, files=files)
    print(response.status_code)
    print(response.text)
