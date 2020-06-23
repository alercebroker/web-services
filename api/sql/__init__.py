from flask_restx import Api

from .AstroObject import api as astro_object

sql_api = Api(title = "ALeRCE API", version="0.0.1", description="Routes for querying ALeRCE database")

sql_api.add_namespace(astro_object, path="/objects")