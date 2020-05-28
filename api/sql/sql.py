from flask import Blueprint
from flask_restful import Api
from .resources.AstroObject import ObjectResource, ObjectListResource
# import resources here


sql_bp = Blueprint('sql', __name__)

sql_api = Api(sql_bp)

sql_api.add_resource(ObjectResource, "/astro_objects/<oid>")
sql_api.add_resource(ObjectListResource, "/astro_objects")
sql_api.add_resource(ObjectResource, "/class/<name>")
sql_api.add_resource(ObjectListResource, "/class")
sql_api.add_resource(ObjectResource, "/classification/<astro_object>/<classifier_name>")
sql_api.add_resource(ObjectListResource, "/classifitacion")
sql_api.add_resource(ObjectResource, "/classifier/<name>")
sql_api.add_resource(ObjectListResource, "/classifier")
sql_api.add_resource(ObjectResource, "/detection/<candid>")
sql_api.add_resource(ObjectListResource, "/detection")
sql_api.add_resource(ObjectResource, "/features_object/<object_id>/<features_version>")
sql_api.add_resource(ObjectListResource, "/features_object")
sql_api.add_resource(ObjectResource, "/magnitude_statistics/<oid>/<magnitude_type>/<fid>")
sql_api.add_resource(ObjectListResource, "/magnitude_statistics")
sql_api.add_resource(ObjectResource, "/non_detection/<oid>/<fid>/<datetime>")
sql_api.add_resource(ObjectListResource, "/non_detection")
sql_api.add_resource(ObjectResource, "/taxonomy/<name>")
sql_api.add_resource(ObjectListResource, "/taxonomy")
