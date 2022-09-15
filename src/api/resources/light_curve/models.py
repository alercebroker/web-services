from flask_restx import fields, Model


detection = Model(
    "Detection",
    {
        "aid": fields.String(description="ALeRCE object identifier"),
        "oid": fields.String(description="Survey object identifier"),
        "tid": fields.String(description="Telescope identifier"),
        "mjd": fields.Float(description="Modified Julian date of observation"),
        "candid": fields.String(
            attribute="_id", description="Candidate identifier"
        ),
        "fid": fields.Integer(
            description="Filter ID (1=g; 2=r; 3=i; 5=c; 6=o)"
        ),
        "isdiffpos": fields.Boolean(
            description="Whether the magnitude difference is positive or not"
        ),
        "mag": fields.Float(description="Magnitude"),
        "e_mag": fields.Float(description="Magnitude uncertainty"),
        "ra": fields.Float(description="Right ascension (J2000) [deg]"),
        "dec": fields.Float(description="Declination (J2000) [deg]"),
        "e_ra": fields.Float(description="Right ascension uncertainty [deg]"),
        "e_dec": fields.Float(description="Declination uncertainty [deg]"),
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
            description="5-sigma limit on magnitude in difference stamp"
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
