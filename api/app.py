from flask import Flask
from flask_restx import Api

from .sql.AstroObject.AstroObject import api as astro_object
from .sql.LightCurve.LightCurve import api as light_curve
from .sql.Magstats.Magstats import api as magstats
from .sql.Probabilities.probabilities import api as probabilities


ztf_api = Api(
    title="ALeRCE API",
    version="0.0.1",
    description="Routes for querying ALeRCE database",
)

ztf_api.add_namespace(astro_object, path="/objects")
ztf_api.add_namespace(light_curve, path="/objects")
ztf_api.add_namespace(magstats, path="/objects")
ztf_api.add_namespace(probabilities, path="/objects")

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    ztf_api.init_app(app)

    with app.app_context():
        from .db import db, session_options
        db.connect(config=app.config["DATABASE"]["SQL"], session_options=session_options, use_scoped=True)
        def cleanup(e):
            db.session.remove()
            return e
        app.teardown_appcontext(cleanup)
    return app