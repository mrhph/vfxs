#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8

import os
import time

import sqlalchemy as sa

from vfxs.models import database, material
from vfxs.config import ASSET_EXPIRE_TIME


class ClearAsset:
    def __init__(self):
        pass

    async def __call__(self, *args, **kwargs):
        current_time = int(time.time() * 1000)
        sql = sa.select(material.c.storage).where(
            sa.and_(
                material.c.is_delete.is_(False),
                sa.between(material.c.expire_time, 1, current_time)
            )
        )
        data = await database.fetch_all(sql)
