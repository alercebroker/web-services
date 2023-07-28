from contextlib import AbstractContextManager
from typing import List, Callable
from core.domain.astroobject_model import AstroObject, Probability
from core.domain.astroobject_queries import GetAstroObjectQuery, GetAstroObjectsQuery
from sqlalchemy import text
from sqlalchemy.orm import Session, aliased
from sqlalchemy.orm.query import RowReturningQuery
from .orm import Object as AstroObjectORM, Probability as ProbabilityORM
from core.shared.sql import Database, Pagination
from ..domain.astroobject_repository import AstroObjectRepository


class AstroObjectSQLRespository(AstroObjectRepository):
    def __init__(self, db_client: Database):
        self.db_client = db_client

    def get_objects(self, query: GetAstroObjectsQuery) -> List[AstroObject]:
        parsed_query = self._parse_objects_query(query)
        try:
            with self.db_client.session() as session:
                join_table = ProbabilityORM
                if parsed_query["filter_probability"]:
                    join_table = (
                        session.query(ProbabilityORM)
                        .filter(ProbabilityORM.classifier_name == query.classifier_name)
                        .filter(ProbabilityORM.classifier_version == query.classifier_version)
                        .filter(ProbabilityORM.ranking == query.ranking)
                        .subquery("probability")
                    )
                    join_table = aliased(ProbabilityORM, join_table)
                db_query = (
                    session.query(AstroObjectORM, join_table)
                    .outerjoin(join_table)
                    .filter(parsed_query["conesearch"])
                    .filter(*parsed_query["filters"])
                    .params(**parsed_query["conesearch_args"])
                )
                parsed_query["order"] = self._order_query(
                    db_query, query.oid, query.order_by, query.order_mode
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
        page, page_size = (query_params.page, query_params.perPage)
        page = 1 if page < 1 else page
        page_size = 10 if page_size < 1 else page_size

        items = query.limit(page_size).offset((page - 1) * page_size).all()
        total = query.order_by(None).limit(50001).count if query_params.count else None

        def parse(db_result: tuple):
            # this assumes that items are a tuple where 0 is the object and 1
            # is the probability
            astro = AstroObject(**db_result[0].__dict__)
            prob = Probability(**db_result[1].__dict__)
            astro.probabilities.append(prob)
            return astro

        return Pagination(
            query, page, page_size, total, list(map(parse, items))
        )

    def _parse_objects_query(self, query: GetAstroObjectsQuery):
        query_dict = query.model_dump(by_alias=True)
        conesearch_args, conesearch = self._parse_conesearch(query_dict)
        filters = self._parse_filters(query_dict)
        filter_probability = all([query.classifier_name, query.classifier_version, query.ranking])

        return {
            "conesearch_args": conesearch_args,
            "conesearch": conesearch,
            "filters": filters,
            "filter_probability": filter_probability,
        }

    def _order_query(self, query: RowReturningQuery, oids: list, order_by: str, order_mode: str):
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
        if filters["classifier_name"]:
            classifier = ProbabilityORM.classifier_name == filters["classifier"]
        if filters["class_name"]:
            class_ = ProbabilityORM.class_name == filters["class"]
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
            probability = ProbabilityORM.probability >= filters["probability"]
        if filters["ranking"]:
            ranking = ProbabilityORM.ranking == filters["ranking"]
        else:
            # Default ranking 1
            ranking = ProbabilityORM.ranking == 1

        if filters["classifier_version"]:
            classifier_version = (
                ProbabilityORM.classifier_version == filters["classifier_version"]
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
