import peewee
import peewee_async
import uuid
import types
from datetime import datetime
from security import verify_password
from playhouse.shortcuts import model_to_dict


class _BaseModel(peewee.Model):
    manager: peewee_async.Manager = None

    @classmethod
    def set_database(cls, db):
        cls._meta.database = db
        for subclass in cls.__subclasses__():
            subclass.set_database(db)
            subclass.create_table()

    @classmethod
    async def list(cls, excl=None):
        records = await _BaseModel.manager.execute(cls.select())
        return [model_to_dict(r, exclude=excl) for r in records]


class User(_BaseModel):
    id = peewee.UUIDField(default=uuid.uuid4(), unique=True, primary_key=True)
    username = peewee.CharField(unique=True)
    password = peewee.CharField()

    @classmethod
    async def authenticate(cls, password, uname=None, uid=None):
        """
        authenticates a user with given password and either of username or user id.
        when both username and user id are present, only username is used for the query.

        :param password: the password in plain text.
        :param uname: username
        :param uid: user id
        :return: the user object if password is correct. None otherwise.
        :raises: AttributeError: if neither username nor user id is provided.
        :raises: User.DoesNotExist: if user is not found by given username or user id.
        """
        query = {}
        if uname is not None:
            query.update(username=uname)
        elif uid is not None:
            query.update(id=uid)
        else:
            raise AttributeError('must provide either "uname" or "uid".')
        user = await _BaseModel.manager.get(User, **query)
        if await verify_password(password, user.password):
            return user
        else:
            return None


class RefreshToken(_BaseModel):

    class Status:
        Active = 'active'
        Expired = 'expired'
        Revoked = 'revoked'

    user_id = peewee.UUIDField(primary_key=True)
    token = peewee.CharField(128, unique=True)
    time_created = peewee.DateTimeField(default=datetime.utcnow)
    status = peewee.CharField(default=Status.Active)


class Application(_BaseModel):

    client_id = peewee.UUIDField(default=uuid.uuid4(), primary_key=True)
    client_secret = peewee.CharField()
    app_name = peewee.CharField()


async def _get_or_none(self, model, *args, **kwargs):
    try:
        return await self.get(model, *args, **kwargs)
    except model.DoesNotExist:
        return None


def setup_pg(app, database, **settings):
    pg_db = peewee_async.PooledPostgresqlDatabase(database, **settings)
    _BaseModel.set_database(pg_db)
    pg_db.set_allow_sync(False)
    app.pg = peewee_async.Manager(pg_db)
    _BaseModel.manager = app.pg
    app.pg.get_or_none = types.MethodType(_get_or_none, app.pg)
    return app.pg
