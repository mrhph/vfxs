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
    Column('name', String(200), nullable=False, comment='name'),
    Column('filename', String(255), nullable=False, comment='文件名'),
    Column('ft', String(50), nullable=False, comment='文件类型'),
    Column('bt', String(50), nullable=False, comment='业务类型'),
    Column('zone', String(200), nullable=False, comment='所属景区'),
    Column('storage', JSON, nullable=False, comment='存储信息'),
    Column('save_time', BigInteger, default=current_timestamp, comment='保存时间'),
    Column('create_time', BigInteger, default=current_timestamp, comment='创建时间'),
    Column('update_time', BigInteger, default=current_timestamp, comment='更新时间'),
    Column('expire_time', BigInteger, default=0, comment='过期时间'),
    Column('is_delete', Boolean, default=False, comment='是否被删除')
)


if __name__ == '__main__':
    import sqlalchemy as sa

    # engine = sa.create_engine(
    #     'sqlite:///./sqlite.db', connect_args={"check_same_thread": False}
    # )
    # metadata.create_all(engine)

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
