from flask_restful import fields, marshal_with, reqparse, Resource
from db_plugins.db.sql import query
from db_plugins.db.sql.models import Classifier, taxonomy_class, Taxonomy, Class
from db_plugins.db.sql.serializers import ClassifierSchema
from flask_restful_swagger_3 import Schema, swagger
from .Class import ClassSchema
from api.db import session


class ClassifierSchema(Schema):
    type = "object"
    resource_fields = {
        "name": fields.String,
        "taxonomy_name": fields.String,
        "classes": fields.List(fields.Nested(ClassSchema.resource_fields)),
    }



class ClassifierResource(Resource):
    def get(self, name):
        result = query(session, Classifier, None, None, None, Classifier.name == name)
        serializer = ClassifierSchema()
        obj = result["results"][0]
        res = serializer.dump(obj)
        return jsonify(res)


class ClassifierListResource(Resource):
    @swagger.doc(
        {
            "summary": "Gets an individual object",
            "description": "long description",
            "responses": {
                "200": {
                    "description": "Ok",
                    "content": {"application/json": {"schema": ClassifierSchema}},
                }
            },
        }
    )
    @marshal_with(ClassifierSchema.resource_fields)
    def get(self):
        results = session.query(Classifier, Taxonomy).join(Taxonomy).all()
        classifiers = []
        for classifier, taxonomy in results:
            classes = taxonomy.classes
            classifier.classes = classes 
            classifiers.append(classifier)
        return classifiers
