from flask import Blueprint
from flask_restful_swagger_3 import Api
from .resources.AstroObject import *
from .resources.Class import *
from .resources.Classification import *
from .resources.Classifier import *
from .resources.Detection import *
from .resources.FeaturesObject import *
from .resources.MagnitudeStatistics import *
from .resources.NonDetection import *
from .resources.Taxonomy import *
# import resources here

sql_bp = Blueprint('sql', __name__)
sql_api = Api(sql_bp, add_api_spec_resource=False)


sql_api.add_resource(ObjectResource, "/astro_objects/<oid>")
sql_api.add_resource(ObjectListResource, "/astro_objects")
sql_api.add_resource(ClassResource, "/class/<name>")
sql_api.add_resource(ClassListResource, "/class")
sql_api.add_resource(ClassificationResource,
                     "/classification/<astro_object>/<classifier_name>")
sql_api.add_resource(
    ClassificationListResource, "/classifitacion")
sql_api.add_resource(ClassifierResource, "/classifier/<name>")
sql_api.add_resource(ClassifierListResource, "/classifier")
sql_api.add_resource(DetectionResource, "/detection/<candid>")
sql_api.add_resource(DetectionListResource, "/detection")
sql_api.add_resource(FeaturesResource,
                     "/features_object/<object_id>/<features_version>")
sql_api.add_resource(FeaturesListResource, "/features_object")
sql_api.add_resource(MagnitudesResource,
                     "/magnitude_statistics/<oid>/<magnitude_type>/<fid>")
sql_api.add_resource(
    MagnitudesListResource, "/magnitude_statistics")
sql_api.add_resource(NonDetectionResource,
                     "/non_detection/<oid>/<fid>/<datetime>")
sql_api.add_resource(NonDetectionListResource, "/non_detection")
sql_api.add_resource(TaxonomyResource, "/taxonomy/<name>")
sql_api.add_resource(TaxonomyListResource, "/taxonomy")
