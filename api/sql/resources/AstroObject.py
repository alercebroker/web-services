from flask_restful import fields, marshal_with, reqparse, Resource
from flask import jsonify
from flask_restful import fields
from flask_restful_swagger_3 import Schema, swagger

from db_plugins.db.sql import query
from db_plugins.db.sql.models import AstroObject, Classification, Xmatch
from api.db import session


class ObjectModel(Schema):
    type = "object"
    resource_fields = {
        "oid": fields.String,
        "ndet": fields.Integer,
        "firstmjd": fields.Float,
        "lastmjd": fields.Float,
        "ra": fields.Float,
        "dec": fields.Float,
        "xmatch_class_catalog": fields.String,
        "class_name": fields.String,
        "probability": fields.Float,
    }


class ResponseModel(Schema):
    type = "array"
    items = ObjectModel


class ObjectResource(Resource):
    @swagger.doc(
        {
            "summary": "Gets an individual object",
            "description": "long description",
            "responses": {
                "200": {
                    "description": "Ok",
                    "content": {"application/json": {"schema": ObjectModel}},
                }
            },
        }
    )
    @marshal_with(ObjectModel.resource_fields)
    def get(self, oid):
        obj = session.query(AstroObject).filter(AstroObject.oid == oid)
        return obj.first()


class ObjectListResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument(
        "classifier",
        type=str,
        dest="classifier",
        location="args",
        help="classifier name",
    )
    parser.add_argument(
        "class", type=str, dest="class", location="args", help="class name"
    )
    parser.add_argument(
        "ndet_min",
        type=int,
        dest="ndet_min",
        location="args",
        help="minimum number of detections",
    )
    parser.add_argument(
        "probability",
        type=float,
        dest="probability",
        location="args",
        help="minimum probability",
    )

    @swagger.doc(
        {
            "summary": "Gets a list of objects",
            "description": "long description",
            "reqparser": {"name": "object query parser", "parser": parser},
            "responses": {
                "200": {
                    "description": "Ok",
                    "content": {"application/json": {"schema": ResponseModel}},
                }
            },
        }
    )
    @marshal_with(ObjectModel.resource_fields)
    def get(self):
        args = self.parser.parse_args()
        params = self.parse_parameters(args)
        ret = []
        for obj, clf in (
            session.query(AstroObject, Classification)
            .join(Classification)
            .filter(*params)
            .limit(10)
            .offset(0)
            .all()
        ):
            ret.append({**obj.__dict__, **clf.__dict__})
        return ret

    def parse_parameters(self, args):
        classifier, class_ = True, True
        for arg in args:
            if args[arg] is not None:
                if arg == "classifier":
                    classifier = Classification.classifier_name == args[arg]
                if arg == "class":
                    class_ = Classification.class_name == args[arg]
        return classifier, class_


class ObjectClassificationsResource(Resource):
    def get(self, oid):
        pass


class ObjectXmatchResource(Resource):
    def get(self, oid):
        pass
