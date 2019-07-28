from sanic import Sanic
from sanauth.entities import setup_pg
from sanauth.handlers import application_handlers, user_handlers, token_handlers
from aioredis import create_redis_pool


def _setup_redis(sanic_app, config):

    async def aio_redis_configure(_app, _loop):
        _app.redis = await create_redis_pool(**config)

    async def close_redis(_app, _loop):
        _app.redis.close()
        await _app.redis.wait_closed()

    sanic_app.listeners['before_server_start'].append(aio_redis_configure)
    sanic_app.listeners['after_server_stop'].append(close_redis)


def sanauth(sanic_app=None, pg_db='app', pg_cfg=dict(), r_cfg=dict()):
    if sanic_app is None:
        sanic_app = Sanic('sanauth')

    sanic_app.pg = setup_pg(
        sanic_app,
        pg_db,
        **pg_cfg
    )

    _setup_redis(sanic_app, r_cfg)
    token_handlers.setup(sanic_app)
    user_handlers.setup(sanic_app)
    application_handlers.setup(sanic_app)

    return sanic_app


if __name__ == "__main__":
    pg_settings = dict(
        user='app-user',
        password='password',
        host='127.0.0.1',
        port=5432
    )
    redis_config = {
        'address': ('127.0.0.1', 6379),
        'minsize': 1,
        'maxsize': 10
    }

    app = sanauth(
        pg_cfg=pg_settings,
        r_cfg=redis_config
    )
    app.run(host="0.0.0.0", port=8000, debug=True)
