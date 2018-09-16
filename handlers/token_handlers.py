
from json import loads, dumps
from sanic import Sanic
from sanic.request import Request
from sanic.response import json
from sanic.log import logger
from sanic.exceptions import SanicException, InvalidUsage
from entities import User, RefreshToken, Application
from time import time
from datetime import datetime
from security import *


class TokenRequestError:
    INVALID_REQUEST = 'invalid_request'
    INVALID_CLIENT = 'invalid_client'
    INVALID_GRANT = 'invalid_grant'
    INVALID_SCOPE = 'invalid_scope'
    UNAUTHORIZED_CLIENT = 'unauthorized_client'
    UNSUPPORTED_GRANT_TYPE = 'unsupported_grant_type'


class UnsuccessfulTokenRequest(SanicException):

    def __init__(self, error: TokenRequestError, error_description='', status_code=400):
        if error == TokenRequestError.INVALID_CLIENT:
            status_code = 401

        msg_dict = dict(
            error=error,
            error_description=error_description
        )

        super().__init__(dumps(msg_dict), status_code)

        self.headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'Cache-Control': 'no-store',
            'Pragma': 'no-cache'
        }


def _get_form_param(request, key):
    try:
        return request.form[key][0]
    except KeyError:
        raise UnsuccessfulTokenRequest(TokenRequestError.INVALID_REQUEST, "missing parameter '%s'" % key)


async def password_auth(request):
    username = _get_form_param(request, 'username')
    password = _get_form_param(request, 'password')
    logger.info('PASSWORD grant for %s.' % username)
    user_ = await request.app.pg.get(User, username=username)
    pwd_verified = await verify_password(password, user_.password)
    if not pwd_verified:
        raise UnsuccessfulTokenRequest(TokenRequestError.INVALID_GRANT, "username and password don't match")
    return pwd_verified, True, 1800, user_


async def refresh_token_auth(request):
    token_str = _get_form_param(request, 'refresh_token')
    found_token = await request.app.pg.get_or_none(RefreshToken, token=token_str)
    if found_token is None:
        raise UnsuccessfulTokenRequest(TokenRequestError.INVALID_GRANT, "invalid refresh token")
    if found_token.status != RefreshToken.Status.Active:
        raise UnsuccessfulTokenRequest(TokenRequestError.INVALID_GRANT, 'token is %s' % found_token.status)

    user_ = await request.app.pg.get(User, id=found_token.user_id)
    return True, True, 1800, user_


async def client_credentials_auth(_request):
    return True, False, 86400, None


auth_chooser = {
    'password': password_auth,
    'refresh_token': refresh_token_auth,
    'client_credentials': client_credentials_auth
}


async def grant_token(request: Request):

    client_id = _get_form_param(request, 'client_id')
    client_secret = _get_form_param(request, 'client_secret')
    application = await request.app.pg.get_or_none(Application, client_id=client_id)

    if application is None:
        raise UnsuccessfulTokenRequest(
            TokenRequestError.INVALID_CLIENT,
            "did not find application with client_id: %s." % client_id
        )

    if not await verify_password(client_secret, application.client_secret):
        raise UnsuccessfulTokenRequest(
            TokenRequestError.INVALID_CLIENT,
            'client_id and client_secret do not match.'
        )

    grant_type = _get_form_param(request, 'grant_type')
    auth_success, issue_refresh_token, token_lifespan, user = await auth_chooser[grant_type](request)

    if auth_success:
        access_token = nonce_gen(64)
        now = datetime.now()

        while await request.app.redis.get(access_token) is not None:
            access_token = nonce_gen(64)
        await request.app.redis.setex(
            access_token,
            token_lifespan,
            dumps(dict(
                username=user.username if isinstance(user, User) else '',
                exp=int(now.strftime('%s')) + token_lifespan
            )))

        if issue_refresh_token:
            refresh_token = nonce_gen(128)

            rt = await request.app.pg.get_or_none(
                RefreshToken,
                user_id=user.id
            )

            if rt is None:
                await request.app.pg.create(RefreshToken,
                                            token=refresh_token,
                                            time_created=now,
                                            status=RefreshToken.Status.Active)
            else:
                rt.token = refresh_token
                rt.time_created = now
                rt.status = RefreshToken.Status.Active
                await request.app.pg.update(rt)

        resp_json = dict(
            access_token=access_token,
            token_type='Bearer',
            expires_in=token_lifespan
        )

        if issue_refresh_token:
            resp_json.update(refresh_token=refresh_token)

        return json(
            resp_json,
            headers={
                'Cache-Control': 'no-store',
                'Pragma': 'no-cache'
            })


async def introspect_token(req: Request):
    if 'token' not in req.form:
        raise InvalidUsage('missing parameter "token"')

    token_info = await req.app.redis.get(req.form.get('token'))

    if token_info is None:
        return json({'active': False})

    token_info = loads(token_info)
    now = time()
    if int(token_info['exp']) < now:
        return json({'active': False})

    token_info.update(active=True)
    return json(token_info)


def setup(app: Sanic):
    app.add_route(grant_token, "/oauth/token", methods=['POST'])
    app.add_route(introspect_token, '/token_info', methods=['POST'])
