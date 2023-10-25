#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import time
import logging

import sqlalchemy as sa

from vfxs.models import database, material


async def clear_asset():
    print('执行文件清理')
    current_time = int(time.time() * 1000)
    sql = sa.select(material.c.storage).where(
        sa.and_(
            material.c.is_delete.is_(False),
            sa.between(material.c.expire_time, 1, current_time)
        )
    )
    data = await database.fetch_all(sql)
    for item in data:
        storage = item.storage
        if storage['type'] == 'systemFile':
            print(f'删除 %s' % storage['info']['path'])
