from flask_restx import Resource, fields, Model

magstats_model = Model(
    "Magstats",
    {
        "fid": fields.Integer(description="Filter ID (1=g; 2=r, 3=i"),
        "stellar": fields.Boolean(
            description="whether the object appears to be unresolved in the given band"
        ),
        "corrected": fields.Boolean(
            description="whether the corrected photometry should be used"
        ),
        "ndet": fields.Integer(description="number of detections in the given band"),
        "ndubious": fields.Integer(description="number of dubious corrections"),
        "magmean": fields.Float(description="the mean magnitude for the given fid"),
        "magmedian": fields.Float(description="the median magnitude for the given fid"),
        "magmax": fields.Float(description="the max magnitude for the given fid"),
        "magmin": fields.Float(description="the min magnitude for the given fid"),
        "magsigma": fields.Float(
            description="magnitude standard deviation for the given fid"
        ),
        "maglast": fields.Float(description="the last magnitude for the given fid"),
        "magfirst": fields.Float(description="the first magnitude for the given fid"),
        "firstmjd": fields.Float(
            description="the time of the first detection in the given fid"
        ),
        "lastmjd": fields.Float(
            description="the time of the last detection in the given fid"
        ),
        "step_id_corr": fields.String(description="correction step pipeline version"),
    },
)
