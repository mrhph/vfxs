#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import time
import typing
import sqlalchemy as sa

from .database import metadata, database


def current_timestamp() -> int:
    return int(time.time() * 1000)


material = sa.Table(
    'material',
    metadata,
    sa.Column('id', sa.Integer, primary_key=True, unique=True, comment='主键'),
    sa.Column('name', sa.String(200), nullable=False, comment='name'),
    sa.Column('filename', sa.String(255), nullable=False, comment='文件名'),
    sa.Column('ft', sa.String(50), nullable=False, comment='文件类型'),
    sa.Column('bt', sa.String(50), nullable=False, comment='业务类型'),
    sa.Column('zone', sa.String(200), nullable=False, comment='所属景区'),
    sa.Column('storage', sa.JSON, nullable=False, comment='存储信息'),
    sa.Column('save_time', sa.BigInteger, default=current_timestamp, comment='保存时间'),
    sa.Column('create_time', sa.BigInteger, default=current_timestamp, comment='创建时间'),
    sa.Column('update_time', sa.BigInteger, default=current_timestamp, comment='更新时间'),
    sa.Column('expire_time', sa.BigInteger, default=0, comment='过期时间'),
    sa.Column('is_delete', sa.Boolean, default=False, comment='是否被删除')
)


async def get_storage_path(zone: str, name: str) -> typing.Union[str, None]:
    sql = sa.select(material.c.storage).where(
        material.c.zone == zone, material.c.name == name
    )
    data = await database.fetch_one(sql)
    if not data:
        return None
    return data.storage['info']['path']

material.get_storage_path = get_storage_path
