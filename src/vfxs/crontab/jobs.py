#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import time

from loguru import logger

from vfxs.config import TMP_DIR, LOG_DIR

logger.add(LOG_DIR.joinpath('clear_vfxs_tmp.log'))


async def clear_vfxs_tmp():
    logger.info('执行文件清理')
    current = time.time()
    for path in TMP_DIR.iterdir():
        if current - path.stat().st_mtime > 86400:  # 1 day
            path.unlink(missing_ok=True)
            logger.info(f'删除{path}')
