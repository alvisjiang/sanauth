import psycopg2
from sanic import Sanic
from sanic.exceptions import NotFound, InvalidUsage
from sanic.request import Request
import sanic.response as resp
from sanauth.security import hash_password
from sanauth.entities import Application
from sanauth.util import get_form_param, nonce_gen
from playhouse.shortcuts import model_to_dict


async def create_app(req: Request):
    new_client = {'app_name': get_form_param(req, 'app_name')}
    client_secret = nonce_gen(32)
    hashed_client_secret = await hash_password(client_secret)
    new_client.update(
        client_secret=hashed_client_secret
    )
    created_app = await req.app.pg.create(Application, **new_client)
    app_dict = model_to_dict(created_app)
    app_dict['client_id'] = str(app_dict['client_id'])
    return resp.json(
        app_dict,
        status=201,
        headers={'location': '/app/%s' % created_app.client_id}
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
    try:
        client = await req.app.pg.get_or_none(Application, client_id=client_id)
    except psycopg2.errors.InvalidTextRepresentation:
        raise InvalidUsage('invalid form of client_id: %s' % client_id)

    if client is None:
        raise NotFound("didn't find application with client_id: %s" % client_id)

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
