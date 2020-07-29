from flask_restx import Resource, fields, Model

object_list_item = Model(
    "Object List Item",
    {
        "oid": fields.String(description="Object identifier"),
        "ndethist": fields.String(
            description="Number of spatially-coincident detections falling within 1.5 arcsec going back to beginning of survey; only detections that fell on the same field and readout-channel ID where the input candidate was observed are counted. All raw detections down to a photometric S/N of ~ 3 are included."
        ),
        "ncovhist": fields.Integer(
            description="Number of times input candidate position fell on any field and readout-channel going back to beginning of survey"
        ),
        "jdstarthist": fields.Float(
            description="Earliest Julian date of epoch corresponding to ndethist [days]"
        ),
        "jdendhist": fields.Float(
            description="Latest Julian date of epoch corresponding to ndethist [days]"
        ),
        "corrected": fields.Boolean(
            description="whether the corrected light curve was computed and can be used"
        ),
        "stellar": fields.Boolean(
            description="whether the object is a likely stellar-like source"
        ),
        "ndet": fields.Integer(description="total number of detections for the object"),
        "firstmjd": fields.Float(description="First detection's modified julian date"),
        "lastmjd": fields.Float(description="Last detection's modified julian date"),
        "deltamjd": fields.Float(
            description="difference between last and first detection date"
        ),
        "meanra": fields.Float(description="Mean Right Ascention"),
        "meandec": fields.Float(description="Mean Declination"),
        "sigmara": fields.Float(description="right ascension standard deviation"),
        "sigmadec": fields.Float(description="declination standard deviation"),
        "class": fields.String(description="Highest probability class", attribute="class_name"),
        "probability": fields.Float(description="Highest probability"),
    },
)
object_item = Model(
    "Single Object",
    {
        "oid": fields.String(description="Object identifier"),
        "ndethist": fields.String(
            description="Number of spatially-coincident detections falling within 1.5 arcsec going back to beginning of survey; only detections that fell on the same field and readout-channel ID where the input candidate was observed are counted. All raw detections down to a photometric S/N of ~ 3 are included."
        ),
        "ncovhist": fields.Integer(
            description="Number of times input candidate position fell on any field and readout-channel going back to beginning of survey"
        ),
        "jdstarthist": fields.Float(
            description="Earliest Julian date of epoch corresponding to ndethist [days]"
        ),
        "jdendhist": fields.Float(
            description="Latest Julian date of epoch corresponding to ndethist [days]"
        ),
        "corrected": fields.Boolean(
            description="whether the corrected light curve was computed and can be used"
        ),
        "stellar": fields.Boolean(
            description="whether the object is a likely stellar-like source"
        ),
        "ndet": fields.Integer(description="total number of detections for the object"),
        "firstmjd": fields.Float(description="First detection's modified julian date"),
        "lastmjd": fields.Float(description="Last detection's modified julian date"),
        "deltamjd": fields.Float(
            description="difference between last and first detection date"
        ),
        "meanra": fields.Float(description="Mean Right Ascention"),
        "meandec": fields.Float(description="Mean Declination"),
        "sigmara": fields.Float(description="right ascension standard deviation"),
        "sigmadec": fields.Float(descriptin="declination standard deviation"),
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
        "items": fields.List(fields.Nested(object_list_item)),
    },
)
