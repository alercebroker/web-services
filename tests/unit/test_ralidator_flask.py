from ralidator_flask.ralidator_flask import RalidatorFlask
from ralidator_core.ralidator_core import Ralidator
from flask import Flask


def test_init():
    # init without app
    rf = RalidatorFlask()
    filters_map = {"test": "ok"}

    assert rf.app is None
    assert rf.filters_map == {}
    app = Flask(__name__)
    app.config["FILTERS_MAP"] = filters_map
    rf.init_app(app)
    assert rf.filters_map == filters_map

    # init with app
    app = Flask(__name__)
    app.config["FILTERS_MAP"] = filters_map
    rf = RalidatorFlask(app)
    assert rf.filters_map == filters_map


def test_set_ralidator_on_context(ralidator_flask, app):
    with app.test_request_context():
        ctx = ralidator_flask.set_ralidator_on_context()
        assert isinstance(ctx.ralidator, Ralidator)


def test_ralidator_property(ralidator_flask, app):
    with app.test_request_context():
        ralidator = ralidator_flask.ralidator
        assert isinstance(ralidator, Ralidator)
