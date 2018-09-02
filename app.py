from sanic import Sanic
from sanic_redis import SanicRedis
from model import setup_pg
import token_handlers
import user_handlers

app = Sanic('oauth')

app.pg = setup_pg('app',
                  user='app-user',
                  password='password',
                  host='127.0.0.1',
                  port=5432)

app.config.update({
    'REDIS': {
        'address': ('127.0.0.1', 6379),
        'minsize': 1,
        'maxsize': 10
    }
})

SanicRedis(app)

token_handlers.setup_token_handlers(app)

user_handlers.setup_user_handler(app)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
