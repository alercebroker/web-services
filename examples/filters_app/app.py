from flask import Flask
from .extensions import ralidator
from .filters import filter_even
from .views import main_views, filtered_views


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["FILTERS_MAP"] = {"filter_even": filter_even}
    app.config["RALIDATOR_SETTINGS"] = {
        "user_api_url": "user_api_url",
        "user_api_token": "user_api_token",
        "secret_key": "secret_key",
    }
    ralidator.init_app(app)
    app.register_blueprint(main_views)
    app.register_blueprint(filtered_views)
    return app
