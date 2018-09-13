from sanic import Sanic
from sanic.exceptions import NotFound
from sanic.request import Request
import sanic.response as resp
from security import nonce_gen, hash_password
from entities import Application
from util import get_form_param
from playhouse.shortcuts import model_to_dict


async def create_app(req: Request):
    new_client = {'app_name': get_form_param(req, 'app_name')}
    client_secret = nonce_gen(32)
    hashed_client_secret = await hash_password(client_secret)
    new_client.update(
        client_secret=hashed_client_secret
    )
    created_app = await req.app.pg.create(Application, **new_client)
    return resp.json(
        model_to_dict(create_app),
        status=201,
        headers={'location': '/app/%s' % str(created_app.client_id)}
    )


async def get_apps(req):
    apps = await req.app.pg.execute(Application.select())
    app_list = []
    for app_ in apps:
        app_dict = model_to_dict(app_)
        app_dict['client_id'] = str(app_dict['client_id'])
        app_list.append(app_dict)
    return resp.json(app_list)


async def get_app(req, client_id):
    client = await req.app.pg.get_or_none(Application, client_id=client_id)
    if client is None:
        raise NotFound

    return resp.json(dict(
        client_id=str(client.client_id),
        app_name=client.app_name
    ))


async def get_new_client_secret(req, client_id):
    client = await req.app.pg.get_or_none(Application, client_id=client_id)
    if client is None:
        raise NotFound

    new_secret = nonce_gen(32)
    hashed_client_secret = await hash_password(new_secret)
    client.client_secret = hashed_client_secret
    await req.app.pg.update(client)
    return resp.json({
        'client_secret': new_secret
    })


async def delete_application(req, client_id):
    try:
        await req.app.pg.delete(Application, client_id=client_id)
    except Application.DoNotExist:
        raise NotFound
    return resp.json({"client_id": client_id})


def setup(app: Sanic):
    app.add_route(create_app, '/app', ['POST'])
    app.add_route(get_apps, '/app')
    app.add_route(get_app, '/app/<client_id:path>')
    app.add_route(delete_application, '/app/<client_id:path>', ['DELETE'])
    app.add_route(get_new_client_secret, '/app/<client_id:path>/new_secret', ['POST'])
