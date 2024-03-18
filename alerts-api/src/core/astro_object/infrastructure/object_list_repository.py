from .repository import Repository
from shared.database.sql import models, Pagination
from sqlalchemy.sql.expression import TextClause
from sqlalchemy import text
from sqlalchemy.orm import aliased, Session
from typing import Union
from returns.result import Success, Failure
from shared.error.exceptions import (
    ServerErrorException,
)


class ObjectListRepository(Repository):
    def __init__(self, session_factory: Session):
        self.session_factory = session_factory

    def get(
        self,
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
            with self.session_factory() as session:
                if not use_default:
                    join_table = models.Probability
                else:
                    join_table = (
                        session.query(models.Probability)
                        .filter(
                            models.Probability.classifier_name
                            == default_classifier
                        )
                        .filter(
                            models.Probability.classifier_version
                            == default_version
                        )
                        .filter(models.Probability.ranking == default_ranking)
                        .subquery("probability")
                    )
                    join_table = aliased(models.Probability, join_table)
                query = (
                    session.query(models.Object, join_table)
                    .outerjoin(join_table)
                    .filter(conesearch)
                    .filter(*filters)
                    .params(**conesearch_args)
                )
                order_statement = self._create_order_statement(
                    query, oids, order_by, order_mode
                )
                q = query.order_by(order_statement)
                pagination = self.paginate(q, page, page_size, count)
                return Success(pagination)
        except Exception as e:
            return Failure(ServerErrorException(e))

    def _create_order_statement(self, query, oids, order_by, order_mode):
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

    def paginate(
        self,
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
        if page < 1:
            page = 1
        if per_page < 0:
            per_page = 10
        items = query.limit(per_page).offset((page - 1) * per_page).all()
        if not count:
            total = None
        else:
            total = query.order_by(None).limit(max_results + 1).count()
        return Pagination(self, page, per_page, total, items)
