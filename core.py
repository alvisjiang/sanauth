from sanic import Sanic
from sanic_redis import SanicRedis
from entities import setup_pg
from handlers import user_handlers, token_handlers, application_handlers


def sanic_oauth(sanic_app=None, pg_db='app', pg_cfg=dict(), r_cfg=dict()):
    if sanic_app is None:
        sanic_app = Sanic('sanic_oauth')

    sanic_app.pg = setup_pg(
        sanic_app,
        pg_db,
        **pg_cfg
    )

    SanicRedis().init_app(sanic_app, redis_config=r_cfg)

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
    app = Sanic('oauth')
    sanic_oauth(
        app,
        pg_cfg=pg_settings,
        r_cfg=redis_config
    )
    app.run(host="0.0.0.0", port=8000, debug=True)
