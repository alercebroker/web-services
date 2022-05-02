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


detection_model = Model(
    "Detection",
    {
        "tid": fields.String(attribute=get_tid),
        "mjd": fields.Float,
        "candid": fields.String,
        "fid": fields.Integer,
        "pid": fields.Integer,
        "diffmaglim": fields.Float,
        "isdiffpos": fields.Integer,
        "nid": fields.Integer,
        "distnr": fields.Float,
        "magpsf": fields.Float(attribute=get_magpsf),
        "magpsf_corr": fields.Float,
        "magpsf_corr_ext": fields.Float,
        "magap": fields.Float,
        "magap_corr": fields.Float,
        "sigmapsf": fields.Float(attribute=get_sigmapsf),
        "sigmapsf_corr": fields.Float,
        "sigmapsf_corr_ext": fields.Float,
        "sigmagap": fields.Float,
        "sigmagap_corr": fields.Float,
        "ra": fields.Float,
        "dec": fields.Float,
        "rb": fields.Float,
        "rbversion": fields.String,
        "drb": fields.Float,
        "magapbig": fields.Float,
        "sigmagapbig": fields.Float,
        "rfid": fields.Integer(attribute=get_rfid),
        "has_stamp": fields.Boolean,
        "corrected": fields.Boolean,
        "dubious": fields.Boolean,
        "candid_alert": fields.String,
        "step_id_corr": fields.String,
        "phase": fields.Float(default=0.0),
        "parent_candid": fields.Integer(attribute=get_parent_candid),
    },
)

non_detection_model = Model(
    "Non Detection",
    {
        "tid": fields.String(attribute=get_tid),
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
