#
# Copyright 2020 BE-GAIA. All Rights Reserved.
#
# coding: utf-8
import asyncio
from concurrent.futures import ProcessPoolExecutor, Executor
from typing import Callable, Optional


class SyncToAsyncWrapper:
    def __init__(
            self,
            func: Callable,
            pool: Optional[Executor] = None,
            loop: Optional[asyncio.Event] = None
    ):
        self.func = func
        self.loop = loop or asyncio.get_event_loop()
        self.pool = pool or ProcessPoolExecutor(max_workers=1)

    async def __call__(self, *args, **kwargs):
        return await self.loop.run_in_executor(self.pool, self.func, *args)
