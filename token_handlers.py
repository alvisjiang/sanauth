
from json import loads, dumps
from sanic import Sanic
from sanic.request import Request
from sanic.response import json
from sanic.log import logger
from sanic.exceptions import Unauthorized, abort
from model import User, RefreshToken
from time import time
from datetime import datetime
from security import *


def setup_token_handlers(app: Sanic):

    @app.route("/oauth/token", methods=['POST'])
    async def grant_token(request: Request):

        async def _password_auth():
            username = request.form.get('username')
            password = request.form.get('password')
            logger.info('PASSWORD grant for %s.' % username)
            user = await app.pg.get(User, username=username)
            pwd_verified = await verify_password(password, user.password)
            return pwd_verified, user

        async def _refresh_token_auth():
            token_str = request.form.get('refresh_token')
            found_token = await app.pg.get_or_none(RefreshToken, token=token_str)
            if found_token is None:
                raise Unauthorized("invalid refresh token")
            if found_token.status != RefreshToken.Status.Active:
                raise Unauthorized('token is %s' % found_token.status)

            user = await app.pg.get(User, id=found_token.user_id)
            return True, user

        job_chooser = {
            'password': _password_auth,
            'refresh_token': _refresh_token_auth
        }

        if 'grant_type' in request.form:
            grant_type = request.form.get('grant_type')
            auth_success, user = await job_chooser[grant_type]()
            if auth_success:
                access_token = nonce_gen(64)
                refresh_token = nonce_gen(128)
                now = datetime.now()
                token_lifespan = 1800

                with await app.redis as r:
                    while await r.get(access_token) is not None:
                        access_token = nonce_gen()
                    await r.setex(
                        access_token,
                        token_lifespan,
                        dumps(dict(
                            username=user.username,
                            exp=int(now.strftime('%s')) + token_lifespan
                        )))

                rt = await app.pg.get_or_none(
                    RefreshToken,
                    user_id=user.id
                )

                if rt is None:
                    await app.pg.create(RefreshToken,
                                        token=refresh_token,
                                        time_created=now,
                                        status=RefreshToken.Status.Active)
                else:
                    rt.token = refresh_token
                    rt.time_created = now
                    rt.status = RefreshToken.Status.Active
                    await app.pg.update(rt)

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

