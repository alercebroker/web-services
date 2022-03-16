from attr import attr
from flask_restx import Resource, fields, Model

class AttributeError(Exception):
    def __init__(self, attribute, raw_response) -> None:
        super().__init__()
        self.attribute = attribute
        self.raw_response = raw_response
    
    def __str__(self) -> str:
        return f"Coudnt find a value for {self.attribute} in {self.raw_response}"

def get_magpsf(raw_response):
    try:
        magpsf = raw_response.magpsf
        return magpsf
    except:
        try:
            mag = raw_response.get("mag")
            return mag
        except:
            raise AttributeError("magpsf", raw_response)

def get_sigmapsf(raw_response):
    try:
        sigmapsf = raw_response.sigmapsf
        return sigmapsf
    except:
        try:
            e_mag = raw_response.get("e_mag")
            return e_mag
        except:
           raise AttributeError("sigmapsf", raw_response) 

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
