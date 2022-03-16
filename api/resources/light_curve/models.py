from flask_restx import Resource, fields, Model
from sqlalchemy import except_

def get_magpsf(raw_response: dict):
    try:
        magpsf = raw_response.magpsf
        return magpsf
    except:
        pass
    try:
        mag = raw_response.get("mag")
        return mag
    except:
        pass

    return None

def get_sigmapsf(raw_response: dict):
    try:
        sigmapsf = raw_response.sigmapsf
        return sigmapsf
    except:
        pass
    try:
        e_mag = raw_response.get("e_mag")
        return e_mag
    except:
        pass

    return None

detection_model = Model(
    "Detection",
    {
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
        "rfid": fields.Integer,
        "has_stamp": fields.Boolean,
        "corrected": fields.Boolean,
        "dubious": fields.Boolean,
        "candid_alert": fields.String,
        "step_id_corr": fields.String,
        "phase": fields.Float,
        "parent_candid": fields.Integer,
    },
)

non_detection_model = Model(
    "Non Detection",
    {"mjd": fields.Float, "fid": fields.Integer, "diffmaglim": fields.Float},
)

light_curve_model = Model(
    "Light Curve",
    {
        "detections": fields.List(fields.Nested(detection_model)),
        "non_detections": fields.List(fields.Nested(non_detection_model)),
    },
)
