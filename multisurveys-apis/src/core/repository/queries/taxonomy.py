from db_plugins.db.sql.models import Taxonomy_ms
from sqlalchemy import select

def query_get_taxonomy(session_ms, classifier_name):

    with session_ms() as session:
        stmt = select(Taxonomy_ms).where(Taxonomy_ms.classifier_name == classifier_name)

        return session.execute(stmt).all()