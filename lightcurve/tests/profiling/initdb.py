from db_plugins.db.sql._connection import PsqlDatabase
from db_plugins.db.sql.models import Object, Detection


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
        detections1 = [
            {
                "candid": 123,
                "oid": "oid1",
                "mjd": 59000,
                "fid": 1,
                "pid": 1,
                "isdiffpos": 1,
                "ra": 10,
                "dec": 20,
                "magpsf": 15,
                "sigmapsf": 0.5,
                "corrected": False,
                "dubious": False,
                "has_stamp": False,
                "step_id_corr": "test",
            },
            {
                "candid": 456,
                "oid": "oid1",
                "mjd": 59001,
                "fid": 2,
                "pid": 1,
                "isdiffpos": 1,
                "ra": 11,
                "dec": 21,
                "magpsf": 14,
                "sigmapsf": 0.4,
                "corrected": False,
                "dubious": False,
                "has_stamp": False,
                "step_id_corr": "test",
            },
        ]
        detections2 = [
            {
                "candid": 123,
                "oid": "oid2",
                "mjd": 59000,
                "fid": 1,
                "pid": 1,
                "isdiffpos": 1,
                "ra": 10,
                "dec": 20,
                "magpsf": 15,
                "sigmapsf": 0.5,
                "corrected": False,
                "dubious": False,
                "has_stamp": False,
                "step_id_corr": "test",
            },
            {
                "candid": 456,
                "oid": "oid2",
                "mjd": 59001,
                "fid": 2,
                "pid": 1,
                "isdiffpos": 1,
                "ra": 11,
                "dec": 21,
                "magpsf": 14,
                "sigmapsf": 0.4,
                "corrected": False,
                "dubious": False,
                "has_stamp": False,
                "step_id_corr": "test",
            },
        ]
        detections1 = [Detection(**det) for det in detections1]
        detections2 = [Detection(**det) for det in detections2]
        session.add_all(detections1)
        session.add_all(detections2)
        session.commit()


def teardown_databases(database: PsqlDatabase):
    database.drop_db()


if __name__ == "__main__":
    db = database()
    populate_databases(db)
