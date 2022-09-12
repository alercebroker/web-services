from flask_restx import fields, Model

from api.resources.features.models import feature
from api.resources.magstats.models import magstats
from api.resources.probabilities.models import probability


xmatch = Model(
    "Cross match",
    {
        "catid": fields.String(description="Catalogue identifier"),
        "oid_catalog": fields.String(
            description="Object identifier in catalogue"
        ),
        "dist": fields.Float(description="Distance in degrees"),
    },
)

object_item = Model(
    "Object List Item",
    {
        "aid": fields.String(attribute="_id", description="ALeRCE object identifier"),
        "ndet": fields.Integer(
            description="Total number of detections for the object"
        ),
        "firstmjd": fields.Float(
            description="First detection's modified Julian date"
        ),
        "lastmjd": fields.Float(
            description="Last detection's modified Julian date"
        ),
        "meanra": fields.Float(description="Mean right ascension"),
        "meandec": fields.Float(description="Mean declination"),
        "classifier_name": fields.String(description="Classifier name"),
        "classifier_version": fields.String(description="Classifier version"),
        "class_name": fields.String(description="Classifier class"),
        "probability": fields.Float(description="Class probability"),
        "ranking": fields.Integer(description="Class ranking"),
    },
)

single_object = Model(
    "Single Object",
    {
        "aid": fields.String(attribute="_id", description="ALeRCE object identifier"),
        "oid": fields.List(
            fields.String, description="Survey object identifiers"
        ),
        "ndet": fields.Integer(
            description="Total number of detections for the object"
        ),
        "firstmjd": fields.Float(
            description="First detection's modified Julian date"
        ),
        "lastmjd": fields.Float(
            description="Last detection's modified Julian date"
        ),
        "meanra": fields.Float(description="Mean right ascension"),
        "meandec": fields.Float(description="Mean declination"),
        "probabilities": fields.List(
            fields.Nested(probability),
            description="Classifier probabilities",
        ),
        "magstats": fields.List(
            fields.Nested(magstats),
            description="Magnitude statistics",
        ),
        "xmatch": fields.List(
            fields.Nested(xmatch),
            description="Cross matches",
        ),
        "features": fields.List(
            fields.Nested(feature),
            description="Features",
        ),
    },
)

object_list = Model(
    "Paginated Object List",
    {
        "total": fields.Integer(description="Total of objects in query"),
        "page": fields.Integer(description="Current page number"),
        "next": fields.Integer(description="Next page"),
        "has_next": fields.Boolean(description="Whether it has a next page"),
        "prev": fields.Integer(description="Previous page number"),
        "has_prev": fields.Boolean(description="Whether it has previous page"),
        "items": fields.List(fields.Nested(object_item)),
    },
)

limit_values = Model(
    "Limit Values",
    {
        "min_ndet": fields.Integer(description="Minimum number of detections"),
        "max_ndet": fields.Integer(description="Maximum number of detections"),
        "min_firstmjd": fields.Float(
            description="First detection's minimum modified Julian date"
        ),
        "max_firstmjd": fields.Float(
            description="First detection's maximum modified Julian date"
        ),
    },
)
