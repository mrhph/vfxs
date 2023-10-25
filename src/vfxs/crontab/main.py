#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import asyncio

from vfxs.crontab.extensions import scheduler
from vfxs.crontab.jobs import clear_asset

if __name__ == '__main__':
    scheduler.add_job(clear_asset, trigger='interval', seconds=5, id='clear_asset')
    scheduler.start()
    asyncio.get_event_loop().run_forever()

