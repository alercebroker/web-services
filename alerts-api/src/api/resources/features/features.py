from flask_restx import Namespace, Resource
from .models import feature_model
from .parsers import fid_parser
from db_plugins.db.sql import models
from werkzeug.exceptions import NotFound
from dependency_injector.wiring import inject, Provide
from api.container import AppContainer

api = Namespace("features", description="Features related operations")
api.models[feature_model.name] = feature_model


@api.route("/<id>/features")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class Features(Resource):
    @api.doc("features")
    @api.expect(fid_parser)
    @api.marshal_list_with(feature_model)
    @inject
    def get(
        self,
        id,
        session_factory=Provide[AppContainer.psql_db.provided.session],
    ):
        """
        Gets list of all features.
        """
        with session_factory() as session:
            args = fid_parser.parse_args()
            obj = (
                session.query(models.Object)
                .filter(models.Object.oid == id)
                .one_or_none()
            )
            if obj:
                q = session.query(models.Feature).filter(
                    models.Feature.oid == obj.oid
                )
                if args.fid is not None:
                    q = q.filter(models.Feature.fid == args.fid)
                if args.version is not None:
                    q = q.filter(models.Feature.version == args.version)
                return q.all()
            else:
                raise NotFound


@api.route("/<id>/features/<name>")
@api.param("id", "The object's identifier")
@api.response(200, "Success")
@api.response(404, "Not found")
class Feature(Resource):
    @api.doc("features")
    @api.expect(fid_parser)
    @api.marshal_with(feature_model)
    @inject
    def get(
        self,
        id,
        name,
        session_factory=Provide[AppContainer.psql_db.provided.session],
    ):
        """
        Gets a single Feature
        """
        args = fid_parser.parse_args()
        with session_factory() as session:
            obj = (
                session.query(models.Object, models.Object.oid)
                .filter(models.Object.oid == id)
                .one_or_none()
            )
            if obj:
                q = (
                    session.query(models.Feature)
                    .filter(models.Feature.name == name)
                    .filter(models.Feature.oid == obj.oid)
                )
                if args.fid is not None:
                    q = q.filter(models.Feature.fid == args.fid)
                if args.version is not None:
                    q = q.filter(models.Feature.version == args.version)
                return q.all()
            else:
                raise NotFound
