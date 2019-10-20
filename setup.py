import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sanauth",
    version="0.0.1a0",
    author="Alvis Jiang",
    author_email="alvisjiang@gmail.com",
    description="An oauth2 server implementation with sanic",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/alvisjiang/sanauth",
    packages=setuptools.find_packages(exclude=['tests']),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'aiopg==1.0.0',
        'aioredis==1.3.0',
        'bcrypt==3.1.7',
        'passlib==1.7.1',
        'peewee==3.11.2',
        'peewee-async==0.6.0a0',
        'psycopg2==2.8.3',
        'sanic==19.6.3',
        'uvloop==0.11.2',
    ],
)
