from sanauth.core import sanauth
from sanauth import util
from functools import wraps
from sanic import Sanic
from uuid import uuid4
from sanic.log import logger


def _arg_injector(arg_type, arg_name, default):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            arg_found = any(isinstance(arg, arg_type) for arg in args) \
                        or (arg_name in kwargs and isinstance(kwargs[arg_name], arg_type))

            if not arg_found:
                kwargs[arg_name] = default() if callable(default) else default

            return func(*args, **kwargs)

        return wrapper

    return decorator


def _make_test_app():
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


@_arg_injector(Sanic, 'sanauth_app', _make_test_app)
def test_create_application(app_name, sanauth_app=None):
    logger.info('testing application creation for app named: %s', app_name)
    params = {
        'app_name': app_name
    }
    req, resp = sanauth_app.test_client.post('/app', data=params)

    assert resp.status == 201
    assert 'location' in resp.headers
    resp_data = resp.json
    assert resp_data
    assert resp_data['app_name'] == app_name
    assert resp_data['client_id']
    assert resp_data['client_secret']
    assert resp_data['client_id'] in resp.headers['location']
    logger.info('all asserts passed for application creation for app named: %s', app_name)
    return resp_data


def test_get_application(app_name, client_id):

    @_arg_injector(Sanic, 'sanauth_app', _make_test_app)
    def test_get_application_400(sanauth_app=None):
        logger.info('testing application query for made up app')
        req, resp = sanauth_app.test_client.get('/app/non-existing-app-client')
        assert resp.status == 400

    @_arg_injector(Sanic, 'sanauth_app', _make_test_app)
    def test_get_application_404(sanauth_app=None):
        req, resp = sanauth_app.test_client.get('/app/%s' % uuid4())
        assert resp.status == 404

    @_arg_injector(Sanic, 'sanauth_app', _make_test_app)
    def test_get_application_200(sanauth_app=None):
        logger.info('testing application query for app: %s', app_name)
        req, resp = sanauth_app.test_client.get(
            '/app/%s' % client_id
        )
        assert resp.status == 200
        logger.info('all asserts passed for application query for app named: %s', app_name)

    test_get_application_400()
    test_get_application_404()
    test_get_application_200()


def test_delete_application(client_id):

    @_arg_injector(Sanic, 'sanauth_app', _make_test_app)
    def test_delete_application_200(sanauth_app=None):
        logger.info('testing application deletion for app: %s', client_id)
        req, resp = sanauth_app.test_client.delete('/app/%s' % client_id)
        assert resp.status == 200
        assert resp.json['client_id'] == client_id
        logger.info('all asserts passed for application deletion for app: %s', client_id)

    @_arg_injector(Sanic, 'sanauth_app', _make_test_app)
    def test_delete_application_400(sanauth_app=None):
        req, resp = sanauth_app.test_client.delete('/app/non-existing-app-client')
        assert resp.status == 400

    @_arg_injector(Sanic, 'sanauth_app', _make_test_app)
    def test_delete_application_404(sanauth_app=None):
        req, resp = sanauth_app.test_client.delete('/app/%s' % uuid4())
        assert resp.status == 404

    test_delete_application_200()
    test_delete_application_400()
    test_delete_application_404()


def test_all(app_name=util.nonce_gen(32)):
    app_data = test_create_application(app_name)
    test_get_application(app_name, app_data['client_id'])
    test_delete_application(app_data['client_id'])


if __name__ == '__main__':
    test_all()
