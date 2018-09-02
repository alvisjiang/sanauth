import random


def nonce_gen(length=22):
    chars = '1234567890' \
            'qwertyuiopasdfghjklzxcvbnm' \
            'QWERTYUIOPASDFGHJKLZXCVBNM' \
            '.\\'
    nonce = ''
    for _ in range(length):
        nonce += random.choice(chars)
    return nonce


def hash_password(pwd):
    """
    https://passlib.readthedocs.io/en/stable/index.html
    :param password:
    :return:
    """
    # salt = nonce_gen()
    return pwd


def verify_password(pwd, hashed_pwd):
    return hash_password(pwd) == hashed_pwd
