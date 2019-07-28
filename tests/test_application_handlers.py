from sanauth import core
import functools


def _sanauth_injector(func):

    @functools.wraps(func)
    def wrapper(sanauth=None, *args, **kwargs):
        if sanauth is None:
            sanauth = make_test_app()
        func(sanauth, *args, **kwargs)

    return wrapper


def make_test_app():
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

    sanauth = core.sanauth(
        pg_cfg=pg_settings,
        r_cfg=redis_config
    )
    return sanauth


@_sanauth_injector
def test_create_app(sanauth=None):
    params = {
        'app_name': 'test_app1'
    }
    req, resp = sanauth.test_client.post('/app', data=params)

    assert resp.status == 201
    assert 'location' in resp.headers
    resp_data = resp.json
    assert resp_data
    assert resp_data['app_name'] == params['app_name']
    assert resp_data['client_id']
    assert resp_data['client_secret']


if __name__ == '__main__':
    test_create_app()
