from flask import Blueprint, jsonify
from ralidator_flask.decorators import (
    set_filters_decorator,
    set_permissions_decorator,
    check_permissions_decorator,
)

main_views = Blueprint("main", __name__)


@main_views.route("/")
def root():
    return "Hello World"


filtered_views = Blueprint("filtered", __name__)

data = [1, 2, 3, 4, 5, 6, 7, 8, 9]


@filtered_views.route("/filtered1")
@set_filters_decorator(["filter_even"])
def filtered1():
    return jsonify(data)
