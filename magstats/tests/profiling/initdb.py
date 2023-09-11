from db_plugins.db.sql._connection import PsqlDatabase
from db_plugins.db.sql.models import Object

def database():
    user = "postgres"
    pwd = "postgres"
    host = "localhost"
    port = "5432"
    db = "postgres"
    database = PsqlDatabase(
        {
            "USER": user,
            "PASSWORD": pwd,
            "HOST": host,
            "PORT": int(port),
            "DB_NAME": db,
        }
    )
    return database


def populate_databases(database):
    database.create_db()
    with database.session() as session:
        object1 = Object(oid="oid1")
        object2 = Object(oid="oid2")
        session.add_all([object1, object2])
        session.commit()
        magstats1 = [

        ]
        magstats2 = [
 
        ]

        session.add_all(magstats1)
        session.add_all(magstats2)
        session.commit()


def teardown_databases(database: PsqlDatabase):
    database.drop_db()


if __name__ == "__main__":
    db = database()
    populate_databases(db)