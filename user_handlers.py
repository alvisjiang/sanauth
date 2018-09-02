from sanic import Sanic
from sanic.request import Request
from sanic.response import text
from sanic.exceptions import abort
from security import hash_password
from model import User


def setup_user_handler(app: Sanic):

    @app.route('/user', methods=['POST'])
    async def user_handler(request: Request):

        username = request.form.get('username')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        if password != confirm:
            abort(400, "passwords don't match.")
        user, created = await app.pg.create_or_get(
            User,
            username=username,
            password=hash_password(password)
        )
        if created:
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
