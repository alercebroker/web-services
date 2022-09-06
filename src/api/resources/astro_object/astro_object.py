from flask_restx import Namespace, Resource
from db_plugins.db.sql import models
from .models import (
    object_list_item,
    object_list,
    object_item,
    limit_values_model,
)
from .parsers import create_parsers
from sqlalchemy import text, func
from sqlalchemy.orm import aliased
from werkzeug.exceptions import NotFound
from dependency_injector.wiring import inject, Provide
from api.container import AppContainer, SQLConnection

api = Namespace("objects", description="Objects related operations")
api.models[object_list_item.name] = object_list_item
api.models[object_list.name] = object_list
api.models[object_item.name] = object_item
api.models[limit_values_model.name] = limit_values_model

(
    filter_parser,
    conesearch_parser,
    order_parser,
    pagination_parser,
) = create_parsers()

DEFAULT_CLASSIFIER = "lc_classifier"
DEFAULT_VERSION = "hierarchical_random_forest_1.0.0"
DEFAULT_RANKING = 1


@api.route("/")
@api.response(200, "Success")
@api.response(404, "Not found")
class ObjectList(Resource):
    @api.doc("list_object")
    @api.expect(
        filter_parser, conesearch_parser, pagination_parser, order_parser
    )
    @api.marshal_with(object_list)
    def get(self):
        """List all objects by given filters"""
        page = self.create_result_page(
            filter_parser, conesearch_parser, pagination_parser, order_parser
        )
        serialized_items = self.serialize_items(page.items)
        return {
            "total": page.total,
            "page": page.page,
            "next": page.next_num,
            "has_next": page.has_next,
            "prev": page.prev_num,
            "has_prev": page.has_prev,
            "items": serialized_items,
        }

    def serialize_items(self, data):
        ret = []
        for obj, prob in data:
            obj = {**obj.__dict__}
            prob = {**prob.__dict__} if prob else {}
            ret.append({**obj, **prob})
        return ret

    def create_result_page(
        self, filter_parser, conesearch_parser, pagination_parser, order_parser
    ):
        filter_args = filter_parser.parse_args()
        conesearch_args = conesearch_parser.parse_args()
        pagination_args = pagination_parser.parse_args()
        order_args = order_parser.parse_args()
        filters = self._parse_filters(filter_args)
        conesearch_args = self._convert_conesearch_args(conesearch_args)
        conesearch = self._create_conesearch_statement(conesearch_args)
        use_default = (
            False
            if (filter_args.get("classifier") is not None)
            or (filter_args.get("classifier_version") is not None)
            or (filter_args.get("ranking") is not None)
            or (filter_args.get("probability") is not None)
            or (filter_args.get("class") is not None)
            else True
        )
        query = self._get_objects(
            filters, conesearch, conesearch_args, default=use_default
        )
        order_statement = self._create_order_statement(
            query, filter_args, order_args
        )
        query = query.order_by(order_statement)
        return query.paginate(
            pagination_args["page"],
            pagination_args["page_size"],
            pagination_args["count"],
        )

    @inject
    def _get_objects(
        self,
        filters,
        conesearch,
        conesearch_args,
        default=True,
        db: SQLConnection = Provide[AppContainer.psql_db],
    ):
        if not default:
            join_table = models.Probability
        else:
            join_table = (
                db.query(models.Probability)
                .filter(
                    models.Probability.classifier_name == DEFAULT_CLASSIFIER
                )
                .filter(
                    models.Probability.classifier_version == DEFAULT_VERSION
                )
                .filter(models.Probability.ranking == DEFAULT_RANKING)
                .subquery("probability")
            )
            join_table = aliased(models.Probability, join_table)

        q = (
            db.query(models.Object, join_table)
            .outerjoin(join_table)
            .filter(conesearch)
            .filter(*filters)
            .params(**conesearch_args)
        )
        return q

    def _create_order_statement(self, query, filter_args, order_args):
        statement = None
        cols = query.column_descriptions
        order_by = order_args["order_by"]
        if order_by:
            for col in cols:
                model = col["type"]
                attr = getattr(model, order_by, None)
                if attr:
                    statement = attr
                    break
            order_mode = order_args["order_mode"]
            if order_mode:
                if order_mode == "ASC":
                    statement = attr.asc()
                if order_mode == "DESC":
                    statement = attr.desc()
        else:
            if filter_args["oid"]:
                oids_order = [f"object.oid!='{x}'" for x in filter_args["oid"]]
                oids_order = ",".join(oids_order)
                statement = text(oids_order)
        return statement

    def _parse_filters(self, args):
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
            classifier = (
                models.Probability.classifier_name == args["classifier"]
            )
        if args["class"]:
            class_ = models.Probability.class_name == args["class"]
        if args["ndet"]:
            ndet = models.Object.ndet >= args["ndet"][0]
            if len(args["ndet"]) > 1:
                ndet = ndet & (models.Object.ndet <= args["ndet"][1])
        if args["firstmjd"]:
            firstmjd = models.Object.firstmjd >= args["firstmjd"][0]
            if len(args["firstmjd"]) > 1:
                firstmjd = firstmjd & (
                    models.Object.firstmjd <= args["firstmjd"][1]
                )
        if args["lastmjd"]:
            lastmjd = models.Object.lastmjd >= args["lastmjd"][0]
            if len(args["lastmjd"]) > 1:
                lastmjd = lastmjd & (
                    models.Object.lastmjd <= args["lastmjd"][1]
                )
        if args["probability"]:
            probability = models.Probability.probability >= args["probability"]
        if args["ranking"]:
            ranking = models.Probability.ranking == args["ranking"]
        elif not args["ranking"] and (
            args["classifier"] or args["class"] or args["classifier_version"]
        ):
            # Default ranking 1
            ranking = models.Probability.ranking == 1

        if args["classifier_version"]:
            classifier_version = (
                models.Probability.classifier_version
                == args["classifier_version"]
            )
        if args["oid"]:
            if len(args["oid"]) == 1:
                filtered_oid = args["oid"][0].replace("*", "%")
                oids = models.Object.oid.like(filtered_oid)
            else:
                oids = models.Object.oid.in_(args["oid"])

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
            radius /= 60.0  # From arcsec to deg
        return {"ra": ra, "dec": dec, "radius": radius}


@api.route("/<id>")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Object not found")
class Object(Resource):
    @api.doc("get_object")
    @api.marshal_with(object_item)
    @inject
    def get(
        self,
        id,
        db: SQLConnection = Provide[AppContainer.psql_db],
    ):
        """Fetch an object given its identifier"""
        result = (
            db.query(models.Object)
            .filter(models.Object.oid == id)
            .one_or_none()
        )
        if result:
            return result
        else:
            raise NotFound("Object not found")


@api.route("/limit_values")
@api.response(200, "Success")
class LimitValues(Resource):
    @api.doc("limit_values")
    @api.marshal_with(limit_values_model)
    @inject
    def get(
        self,
        db: SQLConnection = Provide[AppContainer.psql_db],
    ):
        """Gets min and max values for objects number of detections and detection dates"""
        resp = db.query(
            func.min(models.Object.ndet).label("min_ndet"),
            func.max(models.Object.ndet).label("max_ndet"),
            func.min(models.Object.firstmjd).label("min_firstmjd"),
            func.max(models.Object.firstmjd).label("max_firstmjd"),
        ).first()
        resp = {
            "min_ndet": resp[0],
            "max_ndet": resp[1],
            "min_firstmjd": resp[2],
            "max_firstmjd": resp[3],
        }
        return resp
