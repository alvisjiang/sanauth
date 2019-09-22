import sys
from sanauth.core import sanauth
from uuid import uuid4
import pytest

sys.path.insert(0, '')


def _test_app():
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

    sanauth_app = sanauth(
        pg_cfg=pg_settings,
        r_cfg=redis_config
    )
    return sanauth_app


def _client_and_app():
    test_client = _test_app().test_client
    params = {
        'app_name': 'created_app'
    }
    req, resp = test_client.post('/app', data=params)
    return test_client, resp.json


@pytest.fixture
def client():
    return _test_app().test_client


@pytest.fixture
def client_id():
    client, created_app = _client_and_app()
    return created_app['client_id']


class TestApplicationHandlers(object):

    def test_create_application(self, client, app_name='test_app'):
        params = {
            'app_name': app_name
        }
        req, resp = client.post('/app', data=params)

        assert resp.status == 201
        assert 'location' in resp.headers
        assert resp.json
        assert resp.json['app_name'] == app_name
        assert resp.json['client_id']
        assert resp.json['client_secret']
        assert resp.json['client_id'] in resp.headers['location']

    def test_get_application_400(self, client):
        req, resp = client.get('/app/non-existing-app-client')
        assert resp.status == 400

    def test_get_application_404(self, client):
        req, resp = client.get('/app/%s' % uuid4())
        assert resp.status == 404

    def test_get_application_200(self, client, client_id):
        req, resp = client.get('/app/%s' % client_id)
        assert resp.status == 200

    def test_delete_application_200(self, client, client_id):
        req, resp = client.delete('/app/%s' % client_id)
        assert resp.status == 200
        assert resp.json['client_id'] == client_id

    def test_delete_application_400(self, client):
        req, resp = client.delete('/app/non-existing-app-client')
        assert resp.status == 400

    def test_delete_application_404(self, client):
        req, resp = client.delete('/app/%s' % uuid4())
        assert resp.status == 404
