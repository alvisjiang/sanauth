import peewee
import peewee_async
import uuid
import types
from datetime import datetime


class BaseModel(peewee.Model):
    @classmethod
    def set_database(cls, db):
        cls._meta.database = db
        for subclass in cls.__subclasses__():
            subclass.set_database(db)
            subclass.create_table()


class User(BaseModel):
    id = peewee.UUIDField(default=uuid.uuid4(), unique=True, primary_key=True)
    username = peewee.CharField(unique=True)
    password = peewee.CharField()


class RefreshToken(BaseModel):

    class Status:
        Active = 'active'
        Expired = 'expired'
        Revoked = 'revoked'

    user_id = peewee.UUIDField(primary_key=True)
    token = peewee.CharField(128, unique=True)
    time_created = peewee.DateTimeField(default=datetime.utcnow())
    status = peewee.CharField(default=Status.Active)


class Application(BaseModel):

    client_id = peewee.UUIDField(default=uuid.uuid4(), primary_key=True)
    client_secret = peewee.CharField()
    app_name = peewee.CharField()


async def _get_or_none(self, model, *args, **kwargs):
    try:
        return await self.get(model, *args, **kwargs)
    except model.DoesNotExist:
        return None


def setup_pg(app, database, **settings):
    pg_db = peewee_async.PostgresqlDatabase(database, **settings)
    BaseModel.set_database(pg_db)
    pg_db.set_allow_sync(False)
    app.pg = peewee_async.Manager(pg_db)
    app.pg.get_or_none = types.MethodType(_get_or_none, app.pg)
    return app.pg
