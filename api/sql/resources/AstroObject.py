from flask_restful import fields, marshal_with, reqparse, Resource
from flask import jsonify
from flask_restful_swagger_3 import swagger
from db_plugins.db.sql import query
from db_plugins.db.sql.models import AstroObject
from db_plugins.db.sql.serializers import AstroObjectSchema
parser = reqparse.RequestParser()
parser.add_argument(['oid', 'object_id', 'id'], dest='oid')

# Eventually replace serializer with fields and marshal_with
# Or maybe combine both
fields = {}



class ObjectResource(Resource):
    """
    Astro objects individual resource
    """
    """
    @swagger.doc({
        "summary": "Gets an individual object",
        "description":"long description",
        "parameters":[
            {
                "name": "oid",
                "in": "path",
                "description": "Identifier for the object",
                "required": True,
                "schema":{
                    "type": "string"
                }
            }
        ],
        "requestBody:": {
            "content": {
                "/astro_object/oid": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "oid": {
                                "description": "identifier of the object",
                                "type": "string"
                            },
                            "nobs": {
                                "description": "number of observations",
                                "type": "integer"
                            },
                            "meanra": {
                                "description": "",
                                "type": "integer"
                            },
                            "meandec": {
                                "description": "",
                                "type": "integer"
                            },
                            "sigmara": {
                                "description": "",
                                "type": "integer"
                            },
                            "sigmadec": {
                                "description": "",
                                "type": "integer"
                            },
                            "deltajd": {
                                "description": "",
                                "type": "integer"
                            },
                            "lastmjd": {
                                "description": "last mjd date",
                                "type": "integer"
                            },
                            "firstmjd": {
                                "description": "frist mjd date",
                                "type": "integer"
                            },
                        },
                        "required": ["oid"]
                    }
                }
            }
        },
        "responses":{
            '200': {
                'description': 'Ok',
            }
        }
    }
    )
    """
    def get(self,oid):
        result = query(session, AstroObject, None, None, None, AstroObject.oid == oid)
        serializer = AstroObjectSchema()
        obj = result["results"][0]
        res = serializer.dump(obj)
        return jsonify(res)


class ObjectListResource(Resource):
    """
    Astro object list resource
    """
    """
    @swagger.doc({
        "summary": "Gets a list of objects",
        "description": "long description",
        "requestBody:": {
            "content": {
                "/astro_object": {
                    "schema": {
                        "type": "list",
                        "properties": {
                            "type": "object",
                            "properties": {
                                "oid": {
                                    "description": "identifier of the object",
                                    "type": "string"
                                },
                                "nobs": {
                                    "description": "number of observations",
                                    "type": "integer"
                                },
                                "meanra": {
                                    "description": "",
                                    "type": "integer"
                                },
                                "meandec": {
                                    "description": "",
                                    "type": "integer"
                                },
                                "sigmara": {
                                    "description": "",
                                    "type": "integer"
                                },
                                "sigmadec": {
                                    "description": "",
                                    "type": "integer"
                                },
                                "deltajd": {
                                    "description": "",
                                    "type": "integer"
                                },
                                "lastmjd": {
                                    "description": "last mjd date",
                                    "type": "integer"
                                },
                                "firstmjd": {
                                    "description": "frist mjd date",
                                    "type": "integer"
                                },
                            },
                            "required": ["oid"]
                        }
                    }
                }
            }
        },
        "responses": {
            '200': {
                'description': 'Ok',
            }
        }
    }
    )
    """
    def get(self):
        result = query(session, AstroObject, 1, 1)
        serializer = AstroObjectSchema()
        res = [serializer.dump(obj) for obj in result["results"]]
        return jsonify(res)


class ObjectClassificationsResource(Resource):

    def get(self, oid):
        result = query(session, AstroObject, None, None, None, AstroObject.oid == oid)
        classifications = query(session, Classification, None, None, None, Classification.astro_object == oid)

        serializer = AstroObjectSchema()
        classification_serializer = ClassificationSchema()

        obj = result["results"][0]
        res = serializer.dump(obj)
        obj_classification = classifications["results"][0]
        res_classification = classification_serializer.dump(obj)
        #TODO: como juntar estos datos
        return jsonify(res)


class ObjectXmatchResource(Resource):

    def get(self, oid):
        result = query(session, AstroObject, None, None, None, AstroObject.oid == oid)
        xmatch = query(session, Xmatch, None, None, None, Classification.astro_object == oid)

        serializer = AstroObjectSchema()
        xmatch_serializer = XmatchSchema()

        obj = result["results"][0]
        res = serializer.dump(obj)
        obj_xmatch = xmatch["results"][0]
        res_xmatch = xmatch_serializer.dump(obj)
        #TODO: como juntar estos datos
        return jsonify(res)