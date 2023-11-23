#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
from collections import namedtuple

from qcloud_cos import CosConfig, CosS3Client

from vfxs.config import COS_SECRET_ID, COS_SECRET_KEY, COS_REGION, COS_BUCKET_NAME


CosUploadResult = namedtuple('CosUploadResult', ['Key', 'Bucket', 'Location', 'ETag'])


COS_CONFIG = CosConfig(Region=COS_REGION, SecretId=COS_SECRET_ID, SecretKey=COS_SECRET_KEY, Token=None, Scheme='https')
COS_CLIENT = CosS3Client(COS_CONFIG)


class CosStorage:

    @staticmethod
    def create_bucket(name: str):
        response = COS_CLIENT.list_buckets(Region=COS_REGION)
        buckets = [i['Name'] for i in response['Buckets']['Bucket']]
        if name not in buckets:
            COS_CLIENT.create_bucket(Bucket=name)

    @staticmethod
    def upload_file(path: str, key: str) -> CosUploadResult:
        response = COS_CLIENT.upload_file(
            Bucket=COS_BUCKET_NAME,
            LocalFilePath=path,
            Key=key,
            PartSize=1,
            MAXThread=10,
            EnableMD5=False
        )
        return CosUploadResult(key, response['Bucket'], response['Location'], response['ETag'])

    @staticmethod
    def get_object_url(key: str) -> str:
        return COS_CLIENT.get_object_url(COS_BUCKET_NAME, key)






