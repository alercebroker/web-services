from contextlib import AbstractContextManager
from typing import Callable, Union
from db_plugins.db.sql.models import (
    Object,
    Probability
)

from sqlalchemy.sql.expression import TextClause
from sqlalchemy import select, text
from sqlalchemy.orm import Session, aliased
from ...exceptions import (
    DatabaseError,
    ObjectNotFound,

)

from object_api.models.pagination import Pagination

def query_psql_object(
    oid: str,
    session_factory: Callable[..., AbstractContextManager[Session]],
):
    try:
        assert session_factory is not None
        with session_factory() as session:
            stmt = select(Object).where(Object.oid == oid)
            result = session.execute(stmt)
            first = result.first()
            if first is None:
                raise ObjectNotFound(oid)
            return first[0]
    except ObjectNotFound:
        raise
    except Exception as e:
        raise DatabaseError(e, database="PSQL")
    

def query_psql_object_list(
        session_factory: Callable[..., AbstractContextManager[Session]],
        oids: list,
        page: int,
        page_size: int,
        count: bool,
        order_by: str,
        order_mode: str,
        filters: tuple,
        conesearch_args: dict,
        conesearch: Union[bool, TextClause],
        use_default: bool,
        default_classifier: str,
        default_version: str,
        default_ranking: int,
):
    try:
        with session_factory() as session:
            if not use_default:
                join_table = Probability
            else:
                join_table = (
                    session.query(Probability)
                    .filter(
                        Probability.classifier_name
                        == default_classifier
                    )
                    .filter(
                        Probability.classifier_version
                        == default_version
                    )
                    .filter(Probability.ranking == default_ranking)
                    .subquery("probability")
                )
                join_table = aliased(Probability, join_table)
            query = (
                session.query(Object, join_table)
                .outerjoin(join_table)
                .filter(conesearch)
                .filter(*filters)
                .params(**conesearch_args)
            )
            order_statement = _create_order_statement(
                query, oids, order_by, order_mode
            )
            q = query.order_by(order_statement)
            pagination = paginate(q, page, page_size, count)
            return pagination
    except Exception as e:
        print({str(e)})
        raise Exception(f"Error query")
    
def paginate(
    query,
    page=1,
    per_page=10,
    count=True,
    max_results=50000,
):
    """
    Returns pagination object with the results

    Parameters
    -----------

    page : int
        page or offset of the query
    per_page : int
        number of items per each result page
    count : bool
        whether to count total elements in query
    """
    try:
        if page < 1:
            page = 1
        if per_page < 0:
            per_page = 10
        items = query.limit(per_page).offset((page - 1) * per_page).all()

        if not count:
            total = None
        else:
            total = query.order_by(None).limit(max_results + 1).count()
            
        return Pagination(query=query,page=page, per_page=per_page, total=total, items=items)
    except Exception as e:
        raise Exception(f"Error pagination list: {str(e)}")


def _create_order_statement(query, oids, order_by, order_mode):
    statement = None
    cols = query.column_descriptions
    if order_by:
        for col in cols:
            model = col["type"]
            attr = getattr(model, order_by, None)
            if attr:
                statement = attr
                break
        if order_mode:
            if order_mode == "ASC":
                statement = attr.asc()
            if order_mode == "DESC":
                statement = attr.desc()
    else:
        if oids:
            oids_order = [f"object.oid!='{x}'" for x in oids]
            oids_order = ",".join(oids_order)
            statement = text(oids_order)
    return statement