from flask_restx import Api

from .AstroObject import api as astro_object

sql_api = Api(title = "SQL API", version="0.0.1", description="Routes for querying SQL database")

sql_api.add_namespace(astro_object, path="/objects")