#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import json
import requests


def test_asset_upload():
    url = "http://127.0.0.1:8000/v1.0/zone/aaa/asset"
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
    print(response.request.body.decode())
    print()
    print(response.text)


def test_asset_list():
    url = "http://127.0.0.1:8000/v1.0/zone/aaa/asset"
    response = requests.get(url)
    print(response.json())
