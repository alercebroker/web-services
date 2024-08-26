import os
import time
from db.sql._connection import MockerDatabase
from sqlalchemy import create_engine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == "__main__":
    engine = create_engine(f"sqlite:///{BASE_DIR}/sqlite.db", echo=True)
    model = MockerDatabase(engine=engine)
    model.create_db()
    time.sleep(5)
    model.drop_db()
