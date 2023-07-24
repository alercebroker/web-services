from flask_restx import Namespace, Resource
from .models import (
    object_list_item,
    object_list,
    object_item,
    limit_values_model,
)
from .parsers import create_parsers
from dependency_injector.wiring import inject, Provide
from dependency_injector.providers import Factory
from api.container import AppContainer
from core.astro_object.domain.astro_object_service import GetObjectListPayload
from shared.interface.command import Command
from shared.interface.command import ResultHandler
from shared.database.sql import models
from sqlalchemy import func
from werkzeug.exceptions import NotFound

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
    @inject
    def get(
        self,
        command_factory: Factory[Command] = Provide[
            AppContainer.astro_object_package.get_object_list_command.provider
        ],
        result_handler_factory: Factory[ResultHandler] = Provide[
            AppContainer.view_result_handler.provider
        ],
    ):
        """List all objects by given filters"""
        filter_args = filter_parser.parse_args()
        conesearch_args = conesearch_parser.parse_args()
        pagination_args = pagination_parser.parse_args()
        order_args = order_parser.parse_args()
        handler = result_handler_factory(callback=self.parse_output)
        command = command_factory(
            payload=GetObjectListPayload(
                filter_args,
                pagination_args,
                order_args,
                conesearch_args,
                DEFAULT_CLASSIFIER,
                DEFAULT_VERSION,
                DEFAULT_RANKING,
            ),
            handler=handler,
        )
        command.execute()
        return handler.result

    def parse_output(self, result):
        return {
            "total": result.total,
            "next": result.next_num,
            "has_next": result.has_next,
            "prev": result.prev_num,
            "has_prev": result.has_prev,
            "items": self.serialize_items(result.items),
        }

    def serialize_items(self, data):
        ret = []
        for obj, prob in data:
            obj = {**obj.__dict__}
            prob = {**prob.__dict__} if prob else {}
            ret.append({**obj, **prob})
        return ret


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
        session_factory=Provide[AppContainer.psql_db.provided.session],
    ):
        """Fetch an object given its identifier"""
        with session_factory() as session:
            result = (
                session.query(models.Object)
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
        session_factory=Provide[AppContainer.psql_db.provided.session],
    ):
        """Gets min and max values for objects number of detections and detection dates"""
        with session_factory() as session:
            query = session.query(
                func.min(models.Object.ndet).label("min_ndet"),
                func.max(models.Object.ndet).label("max_ndet"),
                func.min(models.Object.firstmjd).label("min_firstmjd"),
                func.max(models.Object.firstmjd).label("max_firstmjd"),
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
