from sanauth.util import make_async
from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"])


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
