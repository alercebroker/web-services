from flask_restx import fields, Model


detection = Model(
    "Detection",
    {
        "aid": fields.String(description="ALeRCE object identifier"),
        "oid": fields.String(description="Survey object identifier"),
        "tid": fields.String(description="Telescope identifier"),
        "mjd": fields.Float(description="Modified Julian date of observation"),
        "candid": fields.String(description="Candidate identifier"),
        "fid": fields.Integer(description="Filter ID (1=g; 2=r; 3=i)"),
        "isdiffpos": fields.Integer,
        "mag": fields.Float(description="Magnitude of detection"),
        "e_mag": fields.Float(description="Error associated to magnitude"),
        "ra": fields.Float(description="Right ascension"),
        "dec": fields.Float(description="Declination"),
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
        "tid": fields.String(description="Telescope identifier"),
        "mjd": fields.Float(description="Modified Julian date of observation"),
        "fid": fields.Integer(description="Filter ID (1=g; 2=r; 3=i)"),
        "diffmaglim": fields.Float(
            description="Upper limit on magnitude difference with template"
        ),
    },
)

light_curve = Model(
    "Light Curve",
    {
        "detections": fields.List(
            fields.Nested(detection), description="List of detections"
        ),
        "non_detections": fields.List(
            fields.Nested(non_detection), description="List of non-detections"
        ),
    },
)
