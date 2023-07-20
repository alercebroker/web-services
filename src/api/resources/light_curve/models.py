from flask_restx import fields, Model
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
        rfid = raw_response["extra_fields"]["rfid"]

    if rfid and isnan(rfid):
        return None
    else:
        return rfid


def get_tid(raw_response):
    try:
        raw_response["tid"]
        return "atlas"
    except KeyError:
        return "ztf"


class NotNanFloat(fields.Raw):
    def format(self, value):
        return None if isnan(value) else value


detection_model = Model(
    "Detection",
    {
        "tid": fields.String(attribute=get_tid),
        "mjd": NotNanFloat(attribute="mjd"),
        "candid": fields.String,
        "fid": fields.Integer,
        "pid": fields.Integer,
        "diffmaglim": NotNanFloat(attribute="diffmaglim"),
        "isdiffpos": fields.Integer,
        "nid": fields.Integer,
        "distnr": NotNanFloat(attribute="distnr"),
        "magpsf": fields.Float(attribute=get_magpsf),
        "magpsf_corr": NotNanFloat(attribute="magpsf_corr"),
        "magpsf_corr_ext": NotNanFloat(attribute="magpsf_corr_ext"),
        "magap": NotNanFloat(attribute="magap"),
        "magap_corr": NotNanFloat(attribute="magap_corr"),
        "sigmapsf": fields.Float(attribute=get_sigmapsf),
        "sigmapsf_corr": NotNanFloat(attribute="sigmapsf_corr"),
        "sigmapsf_corr_ext": NotNanFloat(attribute="sigmapsf_corr_ext"),
        "sigmagap": NotNanFloat(attribute="sigmagap"),
        "sigmagap_corr": NotNanFloat(attribute="sigmagap_corr"),
        "ra": NotNanFloat(attribute="ra"),
        "dec": NotNanFloat(attribute="dec"),
        "rb": NotNanFloat(attribute="rb"),
        "rbversion": fields.String,
        "drb": NotNanFloat(attribute="drb"),
        "magapbig": NotNanFloat(attribute="magapbig"),
        "sigmagapbig": NotNanFloat(attribute="sigmagapbig"),
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
        "mjd": NotNanFloat(attribute="mjd"),
        "fid": fields.Integer,
        "diffmaglim": NotNanFloat(attribute="diffmaglim"),
    },
)

light_curve_model = Model(
    "Light Curve",
    {
        "detections": fields.List(fields.Nested(detection_model)),
        "non_detections": fields.List(fields.Nested(non_detection_model)),
    },
)
