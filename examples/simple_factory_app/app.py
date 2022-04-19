from flask import Flask, Blueprint
from ralidator_flask.ralidator_flask import RalidatorFlask

simple_page = Blueprint("simple_page", __name__)


@simple_page.route("/")
def hello_world():
    return "Hello World"


ralidator = RalidatorFlask()


def create_app():
    app = Flask(__name__)
    app.config["FILTERS_MAP"] = {}
    app.register_blueprint(simple_page)
    ralidator.init_app(app)
    return app
