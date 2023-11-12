import asyncio
import os
import time
from concurrent.futures import ProcessPoolExecutor


def func(x):
    time.sleep(1)
    if x == 2:
        raise Exception('2 error')
    return x


async def main():
    l = [1, 2, 3]
    with ProcessPoolExecutor(max_workers=len(l)) as pool:
        # result = pool.map(func, l)
        # result = [pool.submit(func, i) for i in l]
        loop = asyncio.get_running_loop()
        try:
            result = await asyncio.gather(*[loop.run_in_executor(pool, func, i) for i in l])
        except Exception as e:
            print(f'处理异常:{e}')
        else:
            print(result)


if __name__ == '__main__':
    t1 = time.perf_counter()
    asyncio.run(main())
    print(time.perf_counter() - t1)


