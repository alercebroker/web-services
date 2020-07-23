from flask import Flask
from flask_restx import Api
from .sql.astro_object.astro_object import api as astro_object
from .sql.light_curve.light_curve import api as light_curve
from .sql.magstats.magstats import api as magstats
from .sql.probabilities.probabilities import api as probabilities
from .sql.features.features import api as features
from .sql.classes.classes import api as classes
from .sql.classifier.classifier import api as classifier
from flask_cors import CORS

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)
    CORS(app)

    with app.app_context():
        from .db import db, session_options

        db.connect(
            config=app.config["DATABASE"]["SQL"],
            session_options=session_options,
            use_scoped=True,
        )

        ztf_api = Api(
            title="ALeRCE API",
            version="0.0.1",
            description="Routes for querying ALeRCE database",
        )

        ztf_api.add_namespace(astro_object, path="/objects")
        ztf_api.add_namespace(light_curve, path="/objects")
        ztf_api.add_namespace(magstats, path="/objects")
        ztf_api.add_namespace(probabilities, path="/objects")
        ztf_api.add_namespace(classes, path="/classes")
        ztf_api.add_namespace(classifier, path="/classifiers")
        ztf_api.add_namespace(features, path="/features")
        ztf_api.init_app(app)

        def cleanup(e):
            db.session.remove()
            return e

        app.teardown_appcontext(cleanup)
    return app
