from flask import Blueprint
from flask_restful import Api
from .resources.AstroObject import ObjectResource, ObjectListResource
# import resources here


sql_bp = Blueprint('sql', __name__)

sql_api = Api(sql_bp)

sql_api.add_resource(ObjectResource, "/astro_objects/<oid>")
sql_api.add_resource(ObjectListResource, "/astro_objects")
# api.add_resource here