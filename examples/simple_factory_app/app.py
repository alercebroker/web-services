from flask import Flask, Blueprint
from ralidator_flask.ralidator_flask import RalidatorFlask

simple_page = Blueprint("simple_page", __name__)


@simple_page.route("/")
def hello_world():
    return "Hello World"


ralidator = RalidatorFlask()

TEST_SECRET_KEY = "test_key"


def create_app():
    app = Flask(__name__)
    app.config["FILTERS_MAP"] = {}
    app.config["RALIDATOR_SETTINGS"] = {
        "USER_API_URL": "user_api_url",
        "USER_API_TOKEN": "user_api_token",
        "SECRET_KEY": TEST_SECRET_KEY,
    }
    app.register_blueprint(simple_page)
    ralidator.init_app(app)
    return app
