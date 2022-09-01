from flask_restx import fields, Model

feature = Model(
    "Feature",
    {
        "name": fields.String(description="ALeRCE feature name"),
        "value": fields.Float(description="Feature value"),
        "fid": fields.Integer(description="Filter ID (1=g; 2=r; 3=i)"),
        "version": fields.String(description="Feature version"),
    },
)
