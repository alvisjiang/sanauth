from sanic import Sanic
from sanic.request import Request
from sanic.response import text, json
from sanic.exceptions import InvalidUsage, NotFound, Unauthorized
from sanauth.security import hash_password
from sanauth.entities import User
from sanauth.util import get_form_param


async def add_user(request: Request):

    username = get_form_param(request, 'username')
    password = get_form_param(request, 'password')
    confirm = get_form_param(request, 'confirm')

    if password != confirm:
        raise InvalidUsage("passwords don't match.")

    user = await request.app.pg.get_or_none(
        User,
        username=username
    )

    if user is None:
        hashed_password = await hash_password(password)
        user = await request.app.pg.create(
            User,
            username=username,
            password=hashed_password
        )
        return text(
            'ok',
            status=201,
            headers={
                'Location': '/user/%s' % str(user.id)
            })
    else:
        return text(
            "username '%s' already exists. Please pick another user name." % username,
            409
        )


async def update_password(req: Request, user_id):
    new_pwd = get_form_param(req, 'new_password')
    old_pwd = get_form_param(req, 'old_password')
    confirm = get_form_param(req, 'confirm')

    if new_pwd != confirm:
        raise InvalidUsage("new_password and confirm don't match.")

    try:
        user = User.authenticate(old_pwd, uid=user_id)
    except User.DoesNotExist:
        raise NotFound

    if user is None:
        raise Unauthorized

    user.password = await hash_password(new_pwd)
    await req.app.pg.update(user)

    return text('password updated')


async def get_users(_req):
    users = await User.list(excl=['password'])
    for user in users:
        user['id'] = str(user['id'])
    return json(users)


def setup(app: Sanic):
    app.add_route(get_users, '/user')
    app.add_route(add_user, '/user', ['POST'])
    app.add_route(update_password, '/user/<user_id:path>', ['PUT'])
