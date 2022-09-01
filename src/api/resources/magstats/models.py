from flask_restx import fields, Model

magstats = Model(
    "Magnitude statistics",
    {
        "fid": fields.Integer(description="Filter ID (1=g; 2=r; 3=i)"),
        "ndet": fields.Integer(
            description="Number of detections in the given filter"
        ),
        "magmean": fields.Float(
            description="Mean magnitude for the given filter"
        ),
        "magmedian": fields.Float(
            description="Median magnitude for the given filter"
        ),
        "magmax": fields.Float(
            description="Maximum magnitude for the given filter"
        ),
        "magmin": fields.Float(
            description="Minimum magnitude for the given filter"
        ),
        "magsigma": fields.Float(
            description="Standard deviation in magnitude for the given filter"
        ),
        "maglast": fields.Float(
            description="Last magnitude for the given filter"
        ),
        "magfirst": fields.Float(
            description="First magnitude for the given filter"
        ),
        "firstmjd": fields.Float(
            description="First detection's modified Julian date in the given filter"
        ),
        "lastmjd": fields.Float(
            description="First detection's modified Julian date in the given filter"
        ),
        "ingestion-step": fields.String(
            description="Ingestion step pipeline version"
        ),
    },
)
