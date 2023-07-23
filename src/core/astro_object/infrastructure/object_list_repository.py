from .repository import Repository
from db_plugins.db.sql.connection import SQLConnection
from db_plugins.db.sql.models import Object as DBPObject, Probability
from sqlalchemy.sql.expression import TextClause
from sqlalchemy import text
from sqlalchemy.orm import aliased
from typing import Union
from returns.result import Success, Failure
from shared.error.exceptions import (
    ClientErrorException,
    ServerErrorException,
)


class ObjectListRepository(Repository):
    def __init__(self, db: SQLConnection):
        self.db = db

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
            if not use_default:
                join_table = Probability
            else:
                join_table = (
                    self.db.query(Probability)
                    .filter(Probability.classifier_name == default_classifier)
                    .filter(Probability.classifier_version == default_version)
                    .filter(Probability.ranking == default_ranking)
                    .subquery("probability")
                )
                join_table = aliased(Probability, join_table)
            query = (
                self.db.query(DBPObject, join_table)
                .outerjoin(join_table)
                .filter(conesearch)
                .filter(*filters)
                .params(**conesearch_args)
            )
            order_statement = self._create_order_statement(
                query, oids, order_by, order_mode
            )
            q = query.order_by(order_statement)
            pagination = q.paginate(page, page_size, count)
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
