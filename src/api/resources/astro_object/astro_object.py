from flask_restx import Namespace, Resource
from db_plugins.db.sql.models import Object as DBPObject, Probability
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
DEFAULT_VERSION = "hierarchical_random_forest_1.1.0"
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
        filters = self.parse_filters(
            filter_parser,
            conesearch_parser,
            pagination_parser,
            order_parser,
        )
        result = self._get_objects(filters)
        serialized_items = self.serialize_items(result.items)
        return {
            "total": result.total,
            "next": result.next_num,
            "has_next": result.has_next,
            "prev": result.prev_num,
            "has_prev": result.has_prev,
            "items": serialized_items,
        }

    def parse_filters(
        self, filter_parser, conesearch_parser, pagination_parser, order_parser
    ):
        filter_args = filter_parser.parse_args()
        conesearch_args = conesearch_parser.parse_args()
        pagination_args = pagination_parser.parse_args()
        order_args = order_parser.parse_args()
        filters = self._convert_filters_to_sqlalchemy_statement(filter_args)
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
        return {
            "filter_args": filter_args,
            "conesearch_args": conesearch_args,
            "pagination_args": pagination_args,
            "order_args": order_args,
            "filters": filters,
            "conesearch_args": conesearch_args,
            "conesearch": conesearch,
            "use_default": use_default,
        }

    def serialize_items(self, data):
        ret = []
        for obj, prob in data:
            obj = {**obj.__dict__}
            prob = {**prob.__dict__} if prob else {}
            ret.append({**obj, **prob})
        return ret

    @inject
    def _get_objects(
        self,
        filters: dict,
        db: SQLConnection = Provide[AppContainer.psql_db],
    ):
        if not filters["use_default"]:
            join_table = Probability
        else:
            join_table = (
                db.query(Probability)
                .filter(Probability.classifier_name == DEFAULT_CLASSIFIER)
                .filter(Probability.classifier_version == DEFAULT_VERSION)
                .filter(Probability.ranking == DEFAULT_RANKING)
                .subquery("probability")
            )
            join_table = aliased(Probability, join_table)

        q = (
            db.query(DBPObject, join_table)
            .outerjoin(join_table)
            .filter(filters["conesearch"])
            .filter(*filters["filters"])
            .params(**filters["conesearch_args"])
        )
        order_statement = self._create_order_statement(
            q, filters["filter_args"], filters["order_args"]
        )
        q = q.order_by(order_statement)
        return q.paginate(
            filters["pagination_args"]["page"],
            filters["pagination_args"]["page_size"],
            filters["pagination_args"]["count"],
        )

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
        result = db.query(DBPObject).filter(DBPObject.oid == id).one_or_none()
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
        query = db.query(
            func.min(DBPObject.ndet).label("min_ndet"),
            func.max(DBPObject.ndet).label("max_ndet"),
            func.min(DBPObject.firstmjd).label("min_firstmjd"),
            func.max(DBPObject.firstmjd).label("max_firstmjd"),
        )
        values = query.first()
        return self.make_response(values)

    def make_response(self, values):
        resp = {
            "min_ndet": values[0],
            "max_ndet": values[1],
            "min_firstmjd": values[2],
            "max_firstmjd": values[3],
        }
        return resp
