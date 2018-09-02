import random
from passlib.context import CryptContext
from asyncio import coroutine

pwd_context = CryptContext(schemes=["bcrypt"])


def nonce_gen(length=64):
    chars = '1234567890' \
            'qwertyuiopasdfghjklzxcvbnm' \
            'QWERTYUIOPASDFGHJKLZXCVBNM' \
            '.\\'
    nonce = ''
    for _ in range(length):
        nonce += random.choice(chars)
    return nonce


@coroutine
def hash_password(pwd):
    """
    https://passlib.readthedocs.io/en/stable/index.html
    :param pwd:
    :return:
    """
    yield pwd_context.hash(pwd)


@coroutine
def verify_password(pwd, hashed_pwd):
    yield pwd_context.verify(pwd, hashed_pwd)
