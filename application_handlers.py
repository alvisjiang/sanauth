from sanic import Sanic
from sanic.exceptions import NotFound
from sanic.request import Request
import sanic.response as resp
from security import nonce_gen, hash_password
from model import Application
from playhouse.shortcuts import model_to_dict


def setup(app: Sanic):

    @app.route('/app', methods=['POST'])
    async def create_app(req: Request):
        new_client = {'app_name': req.form.get('app_name')}
        client_secret = nonce_gen(32)
        hashed_client_secret = await hash_password(client_secret)
        new_client.update(
            client_secret=hashed_client_secret
        )
        created_app = await app.pg.create(Application, **new_client)
        return resp.json(
            model_to_dict(create_app),
            status=201,
            headers={'location': '/app/%s' % str(created_app.client_id)}
        )

    @app.route('/app', methods=['GET'])
    async def get_apps(_req):
        apps = await app.pg.execute(Application.select())
        app_list = []
        for app_ in apps:
            app_.client_id = str(app_.client_id)
            app_list.append(model_to_dict(app_))
        return resp.json(app_list)

    @app.route('/app/<client_id:path>', methods=['GET'])
    async def get_app(req, client_id):
        client = await app.pg.get_or_none(Application, client_id=client_id)
        if client is None:
            raise NotFound

        return resp.json(dict(
            client_id=str(client.client_id),
            app_name=client.app_name
        ))

    @app.route('/app/<client_id:path>/new_secret', methods=['POST'])
    async def get_new_client_secret(_req, client_id):
        client = await app.pg.get_or_none(Application, client_id=client_id)
        if client is None:
            raise NotFound

        new_secret = nonce_gen(32)
        hashed_client_secret = await hash_password(new_secret)
        client.client_secret = hashed_client_secret
        await app.pg.update(client)
        return resp.json({
            'client_secret': new_secret
        })
