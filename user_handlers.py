from sanic import Sanic
from sanic.request import Request
from sanic.response import text
from sanic.exceptions import InvalidUsage, NotFound, Unauthorized
from security import hash_password, verify_password
from model import User


async def add_user(request: Request):

    username = request.form.get('username')
    password = request.form.get('password')
    confirm = request.form.get('confirm')

    if username is None:
        raise InvalidUsage('missing argument "username".')

    if password is None:
        raise InvalidUsage('missing argument "password".')

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
    new_pwd = req.form.get('new_password')
    if new_pwd is None:
        raise InvalidUsage('missing argument "new_password".')

    confirm = req.form.get('confirm')
    if new_pwd != confirm:
        raise InvalidUsage("new_password and confirm don't match.")

    old_pwd = req.form.get('old_password')
    if old_pwd is None:
        raise InvalidUsage('missing argument "old_password".')

    user = await req.app.pg.get_or_none(User, id=user_id)
    if user is None:
        raise NotFound

    if not await verify_password(old_pwd, user.password):
        raise Unauthorized

    user.password = await  hash_password(new_pwd)
    await req.app.pg.update(user)

    return text('password updated')


def setup_user_handler(app: Sanic):
    app.add_route(add_user, '/user', ['POST'])
    app.add_route(update_password, '/user/<user_id:path>', ['PUT'])
