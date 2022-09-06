from flask_restx import fields, Model


detection = Model(
    "Detection",
    {
        "aid": fields.String(description="ALeRCE object identifier"),
        "oid": fields.String(description="Survey object identifier"),
        "tid": fields.String(description="Telescope identifier"),
        "mjd": fields.Float(description="Modified Julian date of observation"),
        "candid": fields.String(description="Candidate identifier"),
        "fid": fields.Integer(
            description="Filter ID (1=g; 2=r; 3=i; 5=c; 6=o)"
        ),
        "isdiffpos": fields.Boolean(
            description="Whether the magnitude difference is positive or not"
        ),
        "mag": fields.Float(description="Magnitude of detection"),
        "e_mag": fields.Float(description="Error associated to magnitude"),
        "ra": fields.Float(description="Right ascension"),
        "dec": fields.Float(description="Declination"),
    },
)

non_detection = Model(
    "Non Detection",
    {
        "aid": fields.String(description="ALeRCE object identifier"),
        "oid": fields.String(description="Survey object identifier"),
        "tid": fields.String(description="Telescope identifier"),
        "mjd": fields.Float(description="Modified Julian date of observation"),
        "fid": fields.Integer(
            description="Filter ID (1=g; 2=r; 3=i; 5=c; 6=o)"
        ),
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
