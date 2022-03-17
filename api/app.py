from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask
from flask_restx import Api
from .resources.astro_object.astro_object import api as astro_object, limiter
from .resources.light_curve.light_curve import api as light_curve
from .resources.magstats.magstats import api as magstats
from .resources.probabilities.probabilities import api as probabilities
from .resources.features.features import api as features
from .resources.classifier.classifier import api as classifier
from flask_cors import CORS
from .extensions import prometheus_metrics
import os
import logging
from .callbacks import after_request, before_request


def create_app(config):
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_host=1, x_prefix=1)
    app.config.from_object(config)
    CORS(app)
    prometheus_metrics.init_app(app)
    # Check if app run trough gunicorn
    is_gunicorn = "gunicorn" in os.environ.get("SERVER_SOFTWARE", "")
    if is_gunicorn:
        gunicorn_logger = logging.getLogger("gunicorn.error")
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

    @app.before_request
    def beforerequest():
        before_request()

    @app.after_request
    def afterrequest(response):
        return after_request(response, app.logger)

    with app.app_context():
        from .database_access.control import DBControl

        db_control = DBControl(
            app_config=app.config["DATABASE"]["APP_CONFIG"],
            psql_config=app.config["DATABASE"]["SQL"],
            mongo_config=app.config["DATABASE"]["MONGO"]
        )
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
        limiter.init_app(app)

        def cleanup(e):
            db_control.cleanup_databases(e)
            return e

        app.teardown_appcontext(cleanup)

    return app
