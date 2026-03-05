from db_plugins.db.sql.models import (SidLut)
from sqlalchemy import select


def query_all_surveys(session_ms):
    with session_ms() as session:
        stmt = select(SidLut)

        surveys = session.execute(stmt).all()

        return surveys