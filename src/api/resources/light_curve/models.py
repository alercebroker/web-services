from flask_restx import fields, Model


detection = Model(
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
        "parent_candid": fields.String,
    },
)

non_detection = Model(
    "Non Detection",
    {
        "tid": fields.String,
        "mjd": fields.Float,
        "fid": fields.Integer,
        "diffmaglim": fields.Float,
    },
)

light_curve = Model(
    "Light Curve",
    {
        "detections": fields.List(fields.Nested(detection)),
        "non_detections": fields.List(fields.Nested(non_detection)),
    },
)
