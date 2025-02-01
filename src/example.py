import asyncio
import logging
import os
from collections.abc import AsyncGenerator, AsyncIterator

import aiomonitor

import aio_mischief


async def infinite_loop() -> None:
    while True:
        print("l")
        await asyncio.sleep(5)


async def infinite_loop_rec(n: int) -> None:
    if n > 0:
        await infinite_loop_rec(n - 1)
        return
    await infinite_loop()


async def generator() -> AsyncGenerator[str]:
    while True:
        yield "g"
        await asyncio.sleep(5)


async def generator_rec(n: int) -> AsyncGenerator[str]:
    if n > 0:
        async for x in generator_rec(n - 1):
            yield x
        return
    async for x in generator():
        yield x


async def generator_loop(n: int) -> None:
    async for x in generator_rec(n):
        print(x)


class Iterator(AsyncIterator[str]):
    def __init__(self):
        self.first = True

    async def __anext__(self) -> str:
        if self.first:
            self.first = False
        else:
            await asyncio.sleep(5)
        return "i"


class ProxyIterator(AsyncIterator[str]):
    def __init__(self, it: AsyncIterator[str]):
        self.it = it

    async def __anext__(self) -> str:
        return await anext(self.it)


def iterator_rec(n: int) -> AsyncIterator[str]:
    if n == 0:
        return Iterator()
    return ProxyIterator(iterator_rec(n - 1))


async def iterator_loop(n: int) -> None:
    async for x in iterator_rec(n):
        print(x)


async def main() -> None:
    logging.basicConfig()
    logging.getLogger("aiomonitor").setLevel(logging.INFO)
    loop = asyncio.get_running_loop()
    with aiomonitor.start_monitor(loop):
        async with asyncio.TaskGroup() as tg:
            tg.create_task(infinite_loop_rec(3))
            tg.create_task(generator_loop(3))
            tg.create_task(iterator_loop(3))


if os.getenv("AIO_MISCHIEF_PATCH"):
    aio_mischief.patch()

asyncio.run(main())
