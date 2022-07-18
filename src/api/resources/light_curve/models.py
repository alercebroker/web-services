from attr import Attribute, attr
from flask_restx import Resource, fields, Model
from math import isnan


def get_magpsf(raw_response):
    try:
        magpsf = raw_response.magpsf
        return magpsf
    except AttributeError:
        mag = raw_response["mag"]
        return mag


def get_sigmapsf(raw_response):
    try:
        sigmapsf = raw_response.sigmapsf
        return sigmapsf
    except AttributeError:
        e_mag = raw_response["e_mag"]
        return e_mag


def get_parent_candid(raw_response):
    try:
        parent_candid = raw_response.parent_candid
    except AttributeError:
        parent_candid = raw_response["parent_candid"]

    if parent_candid and isnan(parent_candid):
        return None
    else:
        return parent_candid


def get_rfid(raw_response):
    try:
        rfid = raw_response.rfid
    except AttributeError:
        rfid = raw_response["rfid"]

    if rfid and isnan(rfid):
        return None
    else:
        return rfid


def get_tid(raw_response):
    try:
        tid = raw_response["tid"]
        return "atlas"
    except KeyError:
        return "ztf"


class NotNanFloat(fields.Raw):
    def format(self, value):
        return None if isnan(value) else value


detection_model = Model(
    "Detection",
    {
        "aid": fields.String,
        "oid": fields.String,
        "tid": fields.String,
        "mjd": fields.Float,
        "candid": fields.String,
        "fid": fields.Integer,
        "isdiffpos": fields.Integer,
        "mag": fields.Float,
        "e_mag": fields.Float,
        "ra": fields.Float,
        "dec": fields.Float,
        "rb": fields.Float,
        "rbversion": fields.String,
        "has_stamp": fields.Boolean,
        "corrected": fields.Boolean,
        "step_id_corr": fields.String,
        "parent_candid": fields.String
    },
)

non_detection_model = Model(
    "Non Detection",
    {
        "tid": fields.String,
        "mjd": fields.Float,
        "fid": fields.Integer,
        "diffmaglim": fields.Float,
    },
)

light_curve_model = Model(
    "Light Curve",
    {
        "detections": fields.List(fields.Nested(detection_model)),
        "non_detections": fields.List(fields.Nested(non_detection_model)),
    },
)
