#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import asyncio

from vfxs.crontab.extensions import scheduler
from vfxs.crontab.jobs import clear_vfxs_tmp

if __name__ == '__main__':
    scheduler.add_job(clear_vfxs_tmp, trigger='cron', hour=5, id='clear_vfxs_tmp')
    # scheduler.add_job(clear_vfxs_tmp, trigger='interval', seconds=5, id='clear_vfxs_tmp')
    scheduler.start()
    asyncio.get_event_loop().run_forever()

