from sqlalchemy import text
from db_plugins.db.sql._connection import PsqlDatabase


def create_q3c_idx(db: PsqlDatabase):
    # CREATE INDEX runs fine inside a transaction.
    with db.session() as session:
        session.execute(
            text("CREATE INDEX IF NOT EXISTS object_q3c_ang2ipix_idx ON object (q3c_ang2ipix(meanra, meandec));")
        )
        session.commit()

    # CLUSTER and ANALYZE must run outside a transaction block.
    with db._engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
        conn.execute(text("CLUSTER object_q3c_ang2ipix_idx ON object;"))
        conn.execute(text("ANALYZE object;"))
