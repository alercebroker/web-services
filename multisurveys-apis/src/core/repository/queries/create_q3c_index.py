from sqlalchemy import text
from db_plugins.db.sql._connection import PsqlDatabase


def create_q3c_idx(db: PsqlDatabase):
    with db.session() as session:
        session.execute(
            text(
                "CREATE INDEX IF NOT EXISTS object_q3c_ang2ipix_idx ON object (q3c_ang2ipix(meanra, meandec));"
            )
        )
        session.execute(text("CLUSTER object_q3c_ang2ipix_idx ON object;"))
        session.execute(text("ANALYZE object;"))
        session.commit()
