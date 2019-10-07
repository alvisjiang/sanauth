import sys
from uuid import uuid4
import pytest


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

    async def test_get_application_200(self, client, created_app):
        client_id = created_app['client_id']
        resp = await client.get('/app/%s' % client_id)
        assert resp.status == 200

    async def test_delete_application_200(self, client, created_app):
        client_id = created_app['client_id']
        resp = await client.delete('/app/%s' % client_id)
        resp_json = await resp.json()
        assert resp_json
        assert resp.status == 200
        assert resp_json['client_id'] == client_id

    async def test_delete_application_400(self, client):
        resp = await client.delete('/app/non-existing-app-client')
        assert resp.status == 400

    async def test_delete_application_404(self, client):
        resp = await client.delete('/app/%s' % uuid4())
        assert resp.status == 404
