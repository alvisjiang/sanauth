import peewee
import peewee_async
import uuid


class BaseModel(peewee.Model):
    @classmethod
    def set_database(cls, db):
        cls._meta.database = db
        for subclass in cls.__subclasses__():
            subclass.set_database(db)


class User(BaseModel):
    id = peewee.UUIDField(default=uuid.uuid4(), unique=True, primary_key=True)
    username = peewee.CharField(unique=True)
    password = peewee.CharField()


class RefreshToken(BaseModel):
    user_id = peewee.ForeignKeyField(User)
    token = peewee.CharField(128)


pg_async = None


def setup_pg(database, **settings):
    pg_db = peewee_async.PostgresqlDatabase(database, **settings)
    BaseModel.set_database(pg_db)
    User.create_table()
    RefreshToken.create_table()
    pg_db.set_allow_sync(False)

    return peewee_async.Manager(pg_db)
