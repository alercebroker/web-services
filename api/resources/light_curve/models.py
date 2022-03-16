from flask_restx import Resource, fields, Model

def get_magpsf(raw_response: dict):
    magpsf = raw_response.get("magpsf")
    if magpsf:
        return magpsf

    mag = raw_response.get("mag")
    if mag:
        return mag

    return None

def get_sigmapsf(raw_response: dict):
    sigmapsf = raw_response.get("sigmapsf")
    if sigmapsf:
        return sigmapsf
        
    e_mag = raw_response.get("e_mag")
    if e_mag:
        return e_mag

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
