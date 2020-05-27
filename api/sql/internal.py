from flask import Blueprint, Response, current_app, request, jsonify, stream_with_context
import requests
from apf.db.sql.models import *
from apf.db.sql import query
from .app import session
import sys
sys.path.append("..")
internal_blueprint = Blueprint(
    'internal', __name__, template_folder='templates')

def remove_key(d):
    del d['_sa_instance_state']
    return d

@internal_blueprint.route("/class")
def get_classes():
    try:
        resp = query(session, Class)
        serialized = [c.__dict__ for c in resp["results"]]
        serialized = [remove_key(c) for c in serialized]
        resp["results"] = serialized
        return jsonify(resp)
    except Exception as e:
        current_app.logger.error(e)
        return Response(e, 500)


@internal_blueprint.route("/class/<string:class_name>")
def get_class():
    pass


@internal_blueprint.route("/taxonomy")
def get_taxonomies():
    pass


@internal_blueprint.route("/taxonomy/<string:taxonomy_name>")
def get_taxonomy():
    pass


@internal_blueprint.route("/classifier")
def get_classifiers():
    pass


@internal_blueprint.route("/classifier/<string:classifier_name>")
def get_classifier():
    pass


@internal_blueprint.route("/astro_object")
def get_astro_objects():
    pass


@internal_blueprint.route("/astro_object/<string:oid>")
def get_astro_object():
    pass


@internal_blueprint.route("/classification")
def get_classifications():
    pass


@internal_blueprint.route("/features")
def get_features():
    pass


@internal_blueprint.route("/features/<string:version>")
def get_features_version():
    pass


@internal_blueprint.route("/magnitude_statistics")
def get_magnitude_statistics():
    pass


@internal_blueprint.route("/non_detections")
def get_non_detections():
    pass


@internal_blueprint.route("/detections")
def get_detections():
    pass


@internal_blueprint.route("/light_curve")
def get_light_curve():
    pass
