from flask import Flask
from .extensions import ralidator
from .views import main_views, permission_views


TEST_SECRET_KEY = "test_key"


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["FILTERS_MAP"] = {}
    app.config["RALIDATOR_SETTINGS"] = {
        "USER_API_URL": "user_api_url",
        "USER_API_TOKEN": "user_api_token",
        "SECRET_KEY": TEST_SECRET_KEY,
    }
    ralidator.init_app(app)
    app.register_blueprint(main_views)
    app.register_blueprint(permission_views)
    return app
