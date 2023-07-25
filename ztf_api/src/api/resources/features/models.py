from flask_restx import fields, Model

feature_model = Model(
    "Feature",
    {
        "name": fields.String(description="ALeRCE Feature value"),
        "value": fields.Float(description="Feature value"),
        "fid": fields.Integer(description="Filter ID (1=g; 2=r, 3=i)"),
        "version": fields.String(description="Feature Version."),
    },
)
