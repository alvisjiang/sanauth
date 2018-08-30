from sanic import Sanic
from sanic.response import json
from sanic.log import logger
from sanic.exceptions import Unauthorized, abort
import uuid
import sanic.request
import peewee
import peewee_async
import random
from passlib.hash import bcrypt_sha256

app = Sanic('oauth')

pg_db = peewee_async.PostgresqlDatabase('app', user='app-user', password='password',
                                        host='127.0.0.1', port=5433)

db = peewee_async.Manager(pg_db)


class BaseModel(peewee.Model):
    class Meta:
        database = pg_db


class User(BaseModel):
    id = peewee.UUIDField(default=uuid.uuid4(), unique=True, primary_key=True)
    username = peewee.CharField(unique=True)
    password = peewee.CharField()


User.create_table()


def nonce_gen(length=22):
    chars = '1234567890' \
            'qwertyuiopasdfghjklzxcvbnm' \
            'QWERTYUIOPASDFGHJKLZXCVBNM' \
            '.\\'
    nonce = ''
    for _ in range(length):
        nonce += random.choice(chars)
    return nonce


def hash_password(password):
    """
    https://passlib.readthedocs.io/en/stable/index.html
    :param password:
    :return:
    """
    # salt = nonce_gen()
    return password


async def verify_password(username, h):
    user = await db.get(User, username=username)
    password = user.password
    logger.debug('password %s', password)
    return password == h


@app.route("/oauth/token", methods=['POST'])
async def grant_token(request: sanic.request.Request):
    # TODO connect user db (postgresql)
    # TODO connect token store (redis)
    async def _password():
        logger.info('PASSWORD grant.')
        username = request.form.get('username')
        password_raw = request.form.get('password')
        password_hashed = hash_password(password_raw)
        return await verify_password(username, password_hashed)

    job_chooser = {
        'password': _password
    }

    if 'grant_type' in request.form:
        auth_success = await job_chooser[request.form.get('grant_type')]()
        if auth_success:
            return json(
                dict(
                    access_token='aaaaa',
                    token_type='bearer',
                    expires_in=3600,
                    refresh_token='bbb'
                ),
                headers={
                    'Cache-Control': 'no-store',
                    'Pragma': 'no-cache'
                })
    raise Unauthorized("username and password don't match")


@app.route('/user/register', methods=['POST'])
async def user_handler(request: sanic.request.Request):
    username = request.form.get('username')
    password = request.form.get('password')
    confirm = request.form.get('confirm')
    if password != confirm:
        abort(400, "passwords don't match.")
    User.create(
        username=username,
        password=hash_password(password)
    )
    return json('ok')


@app.middleware('request')
async def handle_request(request: sanic.request.Request):
    if request.path == 'oauth/token' or request.path == 'user':
        pg_db.connect_async()


@app.middleware('response')
async def handle_response(request, response):
    if not pg_db.is_closed():
        pg_db.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
