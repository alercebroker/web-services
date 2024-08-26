import os
import time
from db.sql._connection import MockerDatabase
from sqlalchemy import create_engine
from sqlalchemy import text

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":

    """ extension by deafult is enabled in public not in all schemas """


    model = MockerDatabase(
        credentials={
            "USER": os.getenv("USER"),
            "PORT": os.getenv("PORT"),
            "DB_NAME": os.getenv("DB_NAME"),
            "PASSWORD": os.getenv("PASSWORD"),
            "HOST": os.getenv("HOST"),
            "SCHEMA": os.getenv("SCHEMA"),
        }
    )

    with model.session() as session:
        with session.begin():
            session.execute("create extension if not exists vector;")
            session.commit()

    model.create_db()
    # time.sleep(5)
    model.drop_db()
