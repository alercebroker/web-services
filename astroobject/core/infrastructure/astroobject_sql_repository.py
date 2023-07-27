from contextlib import AbstractContextManager
from typing import List, Callable
from core.domain.astroobject_model import AstroObject
from core.domain.astroobject_queries import GetAstroObjectQuery
from core.domain.astroobject_model import AstroObject
from core.domain.astroobject_queries import GetAstroObjectsQuery
from sqlalchemy import text
from sqlalchemy.orm import Session, aliased
from sqlalchemy.orm.query import RowReturningQuery
from .orm import Object as AstroObjectORM, Probability
from core.shared.sql import Pagination
from ..domain.astroobject_repository import AstroObjectRepository


class AstroObjectSQLRespository(AstroObjectRepository):
    def __init__(self, db_session: Callable[..., AbstractContextManager[Session]]):
        self.db_session = db_session

    def get_objects(self, query: GetAstroObjectsQuery) -> List[AstroObject]:
        parsed_query = self._parse_objects_query(query)
        try:
            with self.db_session() as session:
                join_table = Probability
                if parsed_query["filter_probability"]:
                    join_table = (
                        session.query(Probability)
                        .filter(Probability.classifier_name == query.classifier)
                        .filter(Probability.classifier_version == query.version)
                        .filter(Probability.ranking == query.ranking)
                        .subquery("probability")
                    )
                    join_table = aliased(Probability, join_table)
                db_query = (
                    session.query(AstroObjectORM, join_table)
                    .outerjoin(join_table)
                    .filter(parsed_query["conesearch"])
                    .filter(*parsed_query["filters"])
                    .params(**parsed_query["conesearch_args"])
                )
                parsed_query["order"] = self._order_query(
                    db_query, query.oids, query.order_by, query.order_mode
                )
                q = db_query.order_by(parsed_query["order"])
                paginated_response = self._paginate(q, query)
                return paginated_response
        except Exception as e:
            print(e)
            raise e

    def get_object(self, query: GetAstroObjectQuery) -> AstroObject:
        raise Exception("Not implemented")

    def _paginate(self, query: RowReturningQuery, query_params: GetAstroObjectsQuery):
        page, page_size = (query_params.page, query_params.page_size)
        page = 1 if page < 1 else page
        page_size = 10 if page_size < 1 else page_size

        items = query.limit(page_size).offset((page - 1) * page_size).all()
        total = query.order_by(None).limit(50001).count if query_params.count else None

        return Pagination(query, page, page_size, total, items)

    def _parse_objects_query(self, query: GetAstroObjectsQuery):
        conesearch_args, conesearch = self._parse_conesearch(query.conesearch)
        filters = self._parse_filters(query.filters.model_dump(by_alias=True))
        filter_probability = all([query.classifier, query.version, query.ranking])

        return {
            "conesearch_args": conesearch_args,
            "conesearch": conesearch,
            "filters": filters,
            "filter_probability": filter_probability,
        }

    def _order_query(self, query: RowReturningQuery, oids: list, order_by, order_mode):
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

    def _parse_conesearch(self, conesearch: dict):
        try:
            ra, dec, radius = (
                conesearch["ra"],
                conesearch["dec"],
                conesearch.get("radius", 30.0),
            )
        except KeyError:
            ra, dec, radius = None, None, None

        conesearch_args = {"ra": ra, "dec": dec, "radius": radius}
        if ra and dec and radius:
            radius /= 3600.0
            return (
                conesearch_args,
                text("q3c_radial_query(meanra, meandec,:ra, :dec, :radius)"),
            )
        else:
            return (conesearch_args, True)

    def _parse_filters(self, filters: dict):  # ?
        (
            classifier,
            classifier_version,
            class_,
            ndet,
            firstmjd,
            lastmjd,
            probability,
            ranking,
            oids,
        ) = (True, True, True, True, True, True, True, True, True)
        if filters["classifier"]:
            classifier = Probability.classifier_name == filters["classifier"]
        if filters["class"]:
            class_ = Probability.class_name == filters["class"]
        if filters["ndet"]:
            ndet = AstroObjectORM.ndet >= filters["ndet"][0]
            if len(filters["ndet"]) > 1:
                ndet = ndet & (AstroObjectORM.ndet <= filters["ndet"][1])
        if filters["firstmjd"]:
            firstmjd = AstroObjectORM.firstmjd >= filters["firstmjd"][0]
            if len(filters["firstmjd"]) > 1:
                firstmjd = firstmjd & (
                    AstroObjectORM.firstmjd <= filters["firstmjd"][1]
                )
        if filters["lastmjd"]:
            lastmjd = AstroObjectORM.lastmjd >= filters["lastmjd"][0]
            if len(filters["lastmjd"]) > 1:
                lastmjd = lastmjd & (AstroObjectORM.lastmjd <= filters["lastmjd"][1])
        if filters["probability"]:
            probability = Probability.probability >= filters["probability"]
        if filters["ranking"]:
            ranking = Probability.ranking == filters["ranking"]
        elif not filters["ranking"] and (
            filters["classifier"] or filters["class"] or filters["classifier_version"]
        ):
            # Default ranking 1
            ranking = Probability.ranking == 1

        if filters["classifier_version"]:
            classifier_version = (
                Probability.classifier_version == filters["classifier_version"]
            )
        if filters["oid"]:
            if len(filters["oid"]) == 1:
                filtered_oid = filters["oid"][0].replace("*", "%")
                oids = AstroObjectORM.oid.like(filtered_oid)
            else:
                oids = AstroObjectORM.oid.in_(filters["oid"])

        return (
            classifier,
            classifier_version,
            class_,
            ndet,
            firstmjd,
            lastmjd,
            probability,
            ranking,
            oids,
        )
