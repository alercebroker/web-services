from db_plugins.db.sql._connection import PsqlDatabase
from db_plugins.db.sql.models import Object,MagStats

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
            {
                "fid": 123,
                "oid": "oid1",
                "stellar": False,
                "corrected": False,
                "ndet": 1,
                "ndubious": 1,
                "dmdt_first": 0.13,
                "dm_first": 0.12,
                "sigmadm_first": 1.4,
                "dt_first": 2.0,
                "magmean": 19.0,
                "magmedian": 20,
                "magmax": 1.4,
                "magmin": 1.4,
                "magsigma": 1.4,
                "maglast": 1.4,
                "magfirst": 1.4,
                "firstmjd": 1.4,
                "lastmjd": 1.4,
                "step_id_corr": "test",
            }
        ]
        magstats2 = [
            {
                "fid": 456,
                "oid": "oid2",
                "stellar": False,
                "corrected": False,
                "ndet": 1,
                "ndubious": 1,
                "dmdt_first": 0.13,
                "dm_first": 0.12,
                "sigmadm_first": 1.4,
                "dt_first": 2.0,
                "magmean": 19.0,
                "magmedian": 20,
                "magmax": 1.4,
                "magmin": 1.4,
                "magsigma": 1.4,
                "maglast": 1.4,
                "magfirst": 1.4,
                "firstmjd": 1.4,
                "lastmjd": 1.4,
                "step_id_corr": "test",
            }
 
        ]

        session.add_all(magstats1)
        session.add_all(magstats2)
        session.commit()


def teardown_databases(database: PsqlDatabase):
    database.drop_db()


if __name__ == "__main__":
    db = database()
    populate_databases(db)