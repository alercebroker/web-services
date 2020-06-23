from flask_restx import Api

from .AstroObject import api as astro_object
from .LightCurve import api as light_curve


ztf_api = Api(
    title="ALeRCE API",
    version="0.0.1",
    description="Routes for querying ALeRCE database",
)

ztf_api.add_namespace(astro_object, path="/objects")
ztf_api.add_namespace(light_curve, path="/objects")

