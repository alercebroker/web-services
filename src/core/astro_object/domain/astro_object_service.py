from dataclasses import dataclass
from core.astro_object.infrastructure.object_list_repository import (
    ObjectListRepository,
)
from db_plugins.db.sql.models import Probability, Object as DBPObject
from sqlalchemy import text


@dataclass
class GetObjectListPayload:
    filter_args: dict
    pagination_args: dict
    order_args: dict
    conesearch_args: dict
    default_classifier: str
    default_version: str
    default_ranking: int


class AstroObjectService:
    def __init__(
        self, object_list_repository: ObjectListRepository, object_repository
    ):
        self.object_list_repository = object_list_repository
        self.object_repository = object_repository

    def get_object_list(self, payload: GetObjectListPayload):
        use_default = self.use_default(payload.filter_args)
        filters = self._convert_filters_to_sqlalchemy_statement(
            payload.filter_args
        )
        conesearch_args = self._convert_conesearch_args(
            payload.conesearch_args
        )
        conesearch = self._create_conesearch_statement(conesearch_args)
        result = self.object_list_repository.get(
            oids=payload.filter_args["oid"],
            page=payload.pagination_args["page"],
            page_size=payload.pagination_args["page_size"],
            count=payload.pagination_args["count"],
            order_by=payload.order_args["order_by"],
            order_mode=payload.order_args["order_mode"],
            filters=filters,
            conesearch_args=conesearch_args,
            conesearch=conesearch,
            use_default=use_default,
            default_classifier=payload.default_classifier,
            default_version=payload.default_version,
            default_ranking=payload.default_ranking,
        )
        return result

    def get_object_by_id(self, payload: str):
        return self.object_repository.get(payload)

    def get_limit_values(self):
        return self.limit_values_repository.get()

    def use_default(self, filter_args):
        return (
            False
            if (filter_args.get("classifier") is not None)
            or (filter_args.get("classifier_version") is not None)
            or (filter_args.get("ranking") is not None)
            or (filter_args.get("probability") is not None)
            or (filter_args.get("class") is not None)
            else True
        )

    def _convert_filters_to_sqlalchemy_statement(self, args):
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
        if args["classifier"]:
            classifier = Probability.classifier_name == args["classifier"]
        if args["class"]:
            class_ = Probability.class_name == args["class"]
        if args["ndet"]:
            ndet = DBPObject.ndet >= args["ndet"][0]
            if len(args["ndet"]) > 1:
                ndet = ndet & (DBPObject.ndet <= args["ndet"][1])
        if args["firstmjd"]:
            firstmjd = DBPObject.firstmjd >= args["firstmjd"][0]
            if len(args["firstmjd"]) > 1:
                firstmjd = firstmjd & (
                    DBPObject.firstmjd <= args["firstmjd"][1]
                )
        if args["lastmjd"]:
            lastmjd = DBPObject.lastmjd >= args["lastmjd"][0]
            if len(args["lastmjd"]) > 1:
                lastmjd = lastmjd & (DBPObject.lastmjd <= args["lastmjd"][1])
        if args["probability"]:
            probability = Probability.probability >= args["probability"]
        if args["ranking"]:
            ranking = Probability.ranking == args["ranking"]
        elif not args["ranking"] and (
            args["classifier"] or args["class"] or args["classifier_version"]
        ):
            # Default ranking 1
            ranking = Probability.ranking == 1

        if args["classifier_version"]:
            classifier_version = (
                Probability.classifier_version == args["classifier_version"]
            )
        if args["oid"]:
            if len(args["oid"]) == 1:
                filtered_oid = args["oid"][0].replace("*", "%")
                oids = DBPObject.oid.like(filtered_oid)
            else:
                oids = DBPObject.oid.in_(args["oid"])

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

    def _create_conesearch_statement(self, args):
        try:
            ra, dec, radius = args["ra"], args["dec"], args["radius"]
        except KeyError:
            ra, dec, radius = None, None, None

        if ra and dec and radius:
            return text("q3c_radial_query(meanra, meandec,:ra, :dec, :radius)")
        else:
            return True

    def _convert_conesearch_args(self, args):
        try:
            ra, dec, radius = args["ra"], args["dec"], args.get("radius")
            if radius is None:
                radius = 30.0
        except KeyError:
            ra, dec, radius = None, None, None

        if ra and dec and radius:
            radius /= 3600.0  # From arcsec to deg
        return {"ra": ra, "dec": dec, "radius": radius}
