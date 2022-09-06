from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask
from flask_restx import Api
from api.resources.astro_object.astro_object import api as astro_object
from api.resources.light_curve.light_curve import api as light_curve
from api.resources.magstats.magstats import api as magstats
from api.resources.probabilities.probabilities import api as probabilities
from api.resources.features.features import api as features
from api.resources.classifier.classifier import api as classifier
from flask_cors import CORS
from api.extensions import prometheus_metrics, ralidator
from api.coverage_ext import Coverage
import os
import logging
from api.callbacks import after_request, before_request
from api.container import AppContainer
from api.filters import get_filters_map


def create_app(config_path):
    container = AppContainer()
    container.config.from_yaml(config_path)
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_host=1, x_prefix=1)
    app.container = container
    app.config["RALIDATOR_SETTINGS"] = container.config.RALIDATOR_SETTINGS()
    app.config["FILTERS_MAP"] = get_filters_map()
    # Check if app run trough gunicorn
    is_gunicorn = "gunicorn" in os.environ.get("SERVER_SOFTWARE", "")
    if is_gunicorn:  # pragma: no cover
        gunicorn_logger = logging.getLogger("gunicorn.error")
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(os.getenv("LOG_LEVEL", gunicorn_logger.level))
    # set up extensions
    CORS(app)
    ralidator.init_app(app)
    prometheus_metrics.init_app(app)
    if os.getenv("EXAMPLES_TESTING"):  # pragma: no cover
        Coverage(app)

    @app.before_request
    def beforerequest():
        before_request()

    @app.after_request
    def afterrequest(response):
        return after_request(response, app.logger)

    with app.app_context():

        db_control = container.db_control()
        db_control.connect_databases()

        description = open("description.md")

        ztf_api = Api(
            title="ALeRCE API",
            version="1.0.0",
            description=description.read(),
        )

        ztf_api.add_namespace(astro_object, path="/objects")
        ztf_api.add_namespace(light_curve, path="/objects")
        ztf_api.add_namespace(magstats, path="/objects")
        ztf_api.add_namespace(probabilities, path="/objects")
        ztf_api.add_namespace(classifier, path="/classifiers")
        ztf_api.add_namespace(features, path="/objects")
        ztf_api.init_app(app)

        def cleanup(e):
            db_control.cleanup_databases(e)
            return e

        app.teardown_appcontext(cleanup)

    return app
