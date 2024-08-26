import os
import time
from db.sql._connection import MockerDatabase
from sqlalchemy import create_engine
from sqlalchemy import text
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    load_dotenv()
    """ extension by deafult is enabled in public not in all schemas """
    credentials = {
        "USER": os.getenv("STAGING_USER"),
        "PORT": os.getenv("STAGING_PORT"),
        "DB_NAME": os.getenv("STAGING_DB_NAME"),
        "PASSWORD": os.getenv("STAGING_PASSWORD"),
        "HOST": os.getenv("STAGING_HOST"),
        "SCHEMA": os.getenv("STAGING_SCHEMA"),
    }

    model = MockerDatabase(credentials=credentials)

    # with model.session() as session:
    #     with session.begin():
    #         session.execute("SET search_path TO alerce,public;")
    #         session.commit()
    #         session.execute(
    #             text("create extension if not exists vector schema alerce;")
    #         )
    #         session.commit()

    model.create_db()
