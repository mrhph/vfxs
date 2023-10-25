#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import pytest

import sqlalchemy as sa
from databases import Database

from vfxs.models.tables import material


metadata = sa.MetaData()


class TestSqlite:
    def __init__(self):
        self.sqlite_file = '/Users/hph/JetBrains/PycharmProjects/vfxs/src/vfxs/models/sqlite.db'
        self.database = Database(self.sqlite_file)

    @pytest.mark.asyncio
    async def setup_class(self):
        await self.database.connect()
        print('连接数据库成功')

    @pytest.mark.asyncio
    async def teardown_class(self):
        await self.database.disconnect()
        print('数据库连接已关闭')

    @pytest.mark.asyncio
    async def test_query_expire_data(self):
        print('aaaaaa')
        sql = sa.select(material.c.storage).where(
            sa.and_(
                material.c.is_delete.is_(False),
                sa.between(material.c.expire_time, 1, 1698200418635)
            )
        )
        data = await self.database.fetch_all(sql)
        print(data)


@pytest.mark.asyncio
async def test_xxx():
    database = Database('sqlite:////Users/hph/JetBrains/PycharmProjects/vfxs/src/vfxs/models/sqlite.db')
    await database.connect()
    sql = sa.select(material.c.storage).where(
        sa.and_(
            material.c.is_delete.is_(False),
            sa.between(material.c.expire_time, 1, 1698200418635)
        )
    )
    data = await database.fetch_all(sql)
    print(data)


