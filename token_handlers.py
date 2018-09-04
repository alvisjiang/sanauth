
from json import loads, dumps
from sanic import Sanic
from sanic.request import Request
from sanic.response import json
from sanic.log import logger
from sanic.exceptions import Unauthorized, abort
from model import User, RefreshToken
from time import time
from security import *


def setup_token_handlers(app: Sanic):

    @app.route("/oauth/token", methods=['POST'])
    async def grant_token(request: Request):
        async def _password_auth():
            username = request.form.get('username')
            password = request.form.get('password')
            logger.info('PASSWORD grant for %s.' % username)
            user = await app.pg.get(User, username=username)
            return await verify_password(password, user.password), user

        job_chooser = {
            'password': _password_auth
        }

        if 'grant_type' in request.form:
            grant_type = request.form.get('grant_type')
            auth_success, user = await job_chooser[grant_type]()
            if auth_success:
                access_token = nonce_gen(64)
                refresh_token = nonce_gen(128)
                now = int(time())
                token_lifespan = 3600
                with await app.redis as r:
                    while await r.get(access_token) is not None:
                        access_token = nonce_gen()
                    await r.set(
                        access_token,
                        dumps(dict(
                            username=user.username,
                            exp=now + token_lifespan
                        )))
                    (rt, created) = await app.pg.create_or_get(
                        RefreshToken,
                        user_id=user.id,
                        token=refresh_token
                    )
                    if not created:
                        await app.pg.update(rt, only=['token'])

                return json(
                    dict(
                        access_token=access_token,
                        token_type='Bearer',
                        expires_in=token_lifespan,
                        refresh_token=refresh_token
                    ),
                    headers={
                        'Cache-Control': 'no-store',
                        'Pragma': 'no-cache'
                    })

        raise Unauthorized("username and password don't match")

    @app.route('/token_info', methods=['POST'])
    async def introspection_handler(req: Request):
        if 'token' not in req.form:
            abort(400, 'missing parameter "token"')
        with await app.redis as r:
            token_info = await r.get(req.form.get('token'))

            if token_info is None:
                return json({'active': False})

            token_info = loads(token_info)
            now = time()
            if int(token_info['exp']) < now:
                return json({'active': False})

            token_info.update(active=True)
            return json(token_info)

