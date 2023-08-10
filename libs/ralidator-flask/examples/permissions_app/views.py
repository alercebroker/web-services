from flask import Blueprint, jsonify
from ralidator_flask.decorators import (
    set_permissions_decorator,
    check_permissions_decorator,
)

main_views = Blueprint("main", __name__)


@main_views.route("/")
def root():
    return "Hello World"


permission_views = Blueprint("permissions", __name__)

data = [1, 2, 3, 4, 5, 6, 7, 8, 9]


@permission_views.route("/restricted_access")
@set_permissions_decorator(["admin"])
@check_permissions_decorator
def restricted_data():
    return jsonify(data)


@permission_views.route("/public_access")
def public_access():
    return jsonify(data)
