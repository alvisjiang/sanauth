import secrets
from sanauth.util import make_async
from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"])


def nonce_gen(length=64):
    chars = '1234567890' \
            'qwertyuiopasdfghjklzxcvbnm' \
            'QWERTYUIOPASDFGHJKLZXCVBNM'
    nonce = ''
    for _ in range(length):
        nonce += secrets.choice(chars)
    return nonce


@make_async
def hash_password(pwd):
    """
    https://passlib.readthedocs.io/en/stable/index.html
    :param pwd:
    :return:
    """
    return _pwd_context.hash(pwd)


@make_async
def verify_password(pwd, hashed_pwd):
    return _pwd_context.verify(pwd, hashed_pwd)
