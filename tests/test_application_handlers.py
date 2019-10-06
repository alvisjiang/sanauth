import sys
from sanauth.core import sanauth
from uuid import uuid4
import pytest
from pytest_postgresql import factories as psql_factories
from pytest_redis import factories as redis_factories


postgresql_my_proc = psql_factories.postgresql_proc()
postgresql_my = psql_factories.postgresql('postgresql_my_proc')
redis_my_proc = redis_factories.redis_proc()
redis_my = redis_factories.redisdb('redis_my_proc')


@pytest.yield_fixture
def app(postgresql_my_proc, postgresql_my, redis_my_proc, redis_my):

    pg_settings = dict(
        user='postgres',
        password='',
        host='127.0.0.1',
        port=5433,
    )

    redis_config = {
        'address': ('127.0.0.1', 6380),
        'minsize': 1,
        'maxsize': 10
    }

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
async def client_and_app(client):
    params = {
        'app_name': 'created_app'
    }
    resp = await client.post('/app', data=params)
    resp_json = await resp.json()
    return client, resp_json


class TestApplicationHandlers(object):

    async def test_create_application(
        self,
        client,
        app_name='test_app'
    ):
        params = {
            'app_name': app_name
        }
        resp = await client.post('/app', data=params)

        assert resp.status == 201
        assert 'location' in resp.headers
        resp_json = await resp.json()
        assert resp_json['app_name'] == app_name
        assert resp_json['client_id']
        assert resp_json['client_secret']
        assert resp_json['client_id'] in resp.headers['location']

    async def test_get_application_400(self, client):
        resp = await client.get('/app/non-existing-app-client')
        assert resp.status == 400

    async def test_get_application_404(self, client):
        resp = await client.get('/app/%s' % uuid4())
        assert resp.status == 404

    async def test_get_application_200(self, client_and_app):
        client = client_and_app[0]
        client_id = client_and_app[1]['client_id']
        resp = await client.get('/app/%s' % client_id)
        assert resp.status == 200

    async def test_delete_application_200(self, client_and_app):
        client = client_and_app[0]
        client_id = client_and_app[1]['client_id']
        resp = await client.delete('/app/%s' % client_id)
        assert resp.status == 200
        resp_json = await resp.json()
        assert resp_json['client_id'] == client_id

    async def test_delete_application_400(self, client):
        resp = await client.delete('/app/non-existing-app-client')
        assert resp.status == 400

    async def test_delete_application_404(self, client):
        resp = await client.delete('/app/%s' % uuid4())
        assert resp.status == 404
