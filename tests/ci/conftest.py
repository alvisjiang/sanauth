import pytest
from pytest_postgresql import factories as psql_factories
from pytest_redis import factories as redis_factories
from sanauth.core import sanauth


@pytest.fixture
def db_settings(request):
    return dict(
        user='app-user',
        password='password',
        host='127.0.0.1',
        port=5432,
    ), dict(
        address=('127.0.0.1', 6379),
        minsize=1,
        maxsize=10
    )


@pytest.fixture
def app(db_settings):
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
