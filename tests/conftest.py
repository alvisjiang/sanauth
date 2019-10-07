import pytest
from pytest_postgresql import factories as psql_factories
from pytest_redis import factories as redis_factories
from sanauth.core import sanauth


postgresql_my_proc = psql_factories.postgresql_proc()
postgresql_my = psql_factories.postgresql('postgresql_my_proc')
redis_my_proc = redis_factories.redis_proc()
redis_my = redis_factories.redisdb('redis_my_proc')


@pytest.fixture
def db_settings(request):
    return dict(
        user='postgres',
        password='',
        host='127.0.0.1',
        port=5433,
    ), dict(
        address=('127.0.0.1', 6380),
        minsize=1,
        maxsize=10
    )


@pytest.fixture
def app(
    db_settings,
    postgresql_my_proc,
    postgresql_my,
    redis_my_proc,
    redis_my
):
    pg_settings, redis_config = db_settings
    sanauth_app = sanauth(
        pg_cfg=pg_settings,
        r_cfg=redis_config
    )
    yield sanauth_app


@pytest.fixture
def app_fixture(loop, app, test_server):
    return loop.run_until_complete(test_server(app))


@pytest.fixture
def client(loop, app, sanic_client):
    return loop.run_until_complete(sanic_client(app))


@pytest.fixture
async def created_app(client):
    params = {
        'app_name': 'created_app'
    }
    resp = await client.post('/app', data=params)
    resp_json = await resp.json()
    return resp_json
