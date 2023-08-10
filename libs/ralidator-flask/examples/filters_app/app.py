from flask import Flask
from .extensions import ralidator
from .filters import filter_even
from .views import main_views, filtered_views


TEST_SECRET_KEY = "test_key"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["FILTERS_MAP"] = {"filter_even": filter_even}
    app.config["RALIDATOR_SETTINGS"] = {
        "USER_API_URL": "user_api_url",
        "USER_API_TOKEN": "user_api_token",
        "SECRET_KEY": TEST_SECRET_KEY,
    }
    ralidator.init_app(app)
    app.register_blueprint(main_views)
    app.register_blueprint(filtered_views)
    return app
