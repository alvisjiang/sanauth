import asyncio
import functools


def make_async(func):

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if kwargs:
            raise Exception('kwargs are not supported by run_in_executor')
        return await asyncio.get_event_loop().run_in_executor(None, func, *args)

    return wrapper
