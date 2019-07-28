from sanic.exceptions import InvalidUsage
from sanic.request import Request
import asyncio
import functools
import secrets


def make_async(func):
    """
    runs the sync function in executor by running loop.run_in_executor().
    :param func:
    :return:
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        if kwargs:
            raise Exception('kwargs are not supported by run_in_executor')
        return await asyncio.get_event_loop().run_in_executor(None, func, *args)

    return wrapper


def get_form_param(req, key, default=None):
    try:
        return req.form[key][0]
    except KeyError:
        if default is not None:
            return default
        raise InvalidUsage("missing parameter '%s'." % key)


def get_query_arg(req: Request, key, default=None):
    try:
        return req.args[key][0]
    except KeyError:
        if default is not None:
            return default
        raise InvalidUsage("missing argument '%s'." % key)


def nonce_gen(length=64):
    chars = '1234567890' \
            'qwertyuiopasdfghjklzxcvbnm' \
            'QWERTYUIOPASDFGHJKLZXCVBNM'
    nonce = ''
    for _ in range(length):
        nonce += secrets.choice(chars)
    return nonce
