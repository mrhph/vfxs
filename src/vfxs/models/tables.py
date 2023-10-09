#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import time

from sqlalchemy import Table, Column, Integer, String, JSON, BigInteger, Boolean

from .database import metadata

# metadata = MetaData()


def current_timestamp() -> int:
    return int(time.time() * 1000)


material = Table(
    'material',
    metadata,
    Column('id', Integer, primary_key=True, unique=True, comment='主键'),
    Column('name', String(200), nullable=False),
    Column('filename', String(255), nullable=False),
    Column('type', String(50), nullable=False),
    Column('zone', String(200), nullable=False),
    Column('storage', JSON, nullable=False),
    Column('save_time', BigInteger, default=current_timestamp),
    Column('expire_time', BigInteger, default=3600*48),
    Column('create_time', BigInteger, default=current_timestamp),
    Column('is_delete', Boolean, default=False)
)


if __name__ == '__main__':
    import sqlalchemy as sa

    async def main():
        from databases import Database
        db = Database("sqlite:///./sql_app.db")
        await db.connect()
        # query = sa.insert(material)
        # values = [
        #     dict(name='ttt3', filename='ttt.mp3', type='mp3', zone='z', save_info={}),
        #     dict(name='ttt4', filename='ttt.mp3', type='mp3', zone='z', save_info={})
        # ]
        # print(await db.execute_many(query, values))
        query = sa.select(material.c.storage).where(material.c.name == 'ttt3')
        obj = await db.fetch_one(query)
        print(obj.storage)

    import asyncio
    asyncio.run(main())
