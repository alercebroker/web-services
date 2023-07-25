from flask_restx import fields, Model

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
        "mjdstarthist": fields.Float(
            description="Earliest Modified Julian date of epoch corresponding to ndethist [days]"
        ),
        "mjdendhist": fields.Float(
            description="Latest Modified Julian date of epoch corresponding to ndethist [days]"
        ),
        "corrected": fields.Boolean(
            description="whether the corrected light curve was computed and can be used"
        ),
        "stellar": fields.Boolean(
            description="whether the object is a likely stellar-like source"
        ),
        "ndet": fields.Integer(
            description="total number of detections for the object"
        ),
        "g_r_max": fields.Float(
            description="difference between the minimum g and r band difference magnitudes"
        ),
        "g_r_max_corr": fields.Float(
            description="difference between the minimum g and r band corrected magnitudes"
        ),
        "g_r_mean": fields.Float(
            description="difference between the mean g and r band difference magnitudes"
        ),
        "g_r_mean_corr": fields.Float(
            description="difference between the mean g and r band corrected magnitudes"
        ),
        "firstmjd": fields.Float(
            description="First detection's modified julian date"
        ),
        "lastmjd": fields.Float(
            description="Last detection's modified julian date"
        ),
        "deltajd": fields.Float(
            description="difference between last and first detection date"
        ),
        "meanra": fields.Float(description="Mean Right Ascention"),
        "meandec": fields.Float(description="Mean Declination"),
        "sigmara": fields.Float(
            description="right ascension standard deviation"
        ),
        "sigmadec": fields.Float(description="declination standard deviation"),
        "class": fields.String(
            description="Highest probability class or according to specified ranking",
            attribute="class_name",
        ),
        "classifier": fields.String(
            description="Classifier name.", attribute="classifier_name"
        ),
        "probability": fields.Float(
            description="Highest probability or according to specified ranking"
        ),
        "step_id_corr": fields.String(
            description="correction step pipeline version"
        ),
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
        "mjdstarthist": fields.Float(
            description="Earliest Modified Julian date of epoch corresponding to ndethist [days]"
        ),
        "mjdendhist": fields.Float(
            description="Latest Modified Julian date of epoch corresponding to ndethist [days]"
        ),
        "corrected": fields.Boolean(
            description="whether the corrected light curve was computed and can be used"
        ),
        "stellar": fields.Boolean(
            description="whether the object is a likely stellar-like source"
        ),
        "ndet": fields.Integer(
            description="total number of detections for the object"
        ),
        "g_r_max": fields.Float(
            description="difference between the minimum g and r band difference magnitudes"
        ),
        "g_r_max_corr": fields.Float(
            description="difference between the minimum g and r band corrected magnitudes"
        ),
        "g_r_mean": fields.Float(
            description="difference between the mean g and r band difference magnitudes"
        ),
        "g_r_mean_corr": fields.Float(
            description="difference between the mean g and r band corrected magnitudes"
        ),
        "firstmjd": fields.Float(
            description="First detection's modified julian date"
        ),
        "lastmjd": fields.Float(
            description="Last detection's modified julian date"
        ),
        "deltajd": fields.Float(
            description="difference between last and first detection date"
        ),
        "meanra": fields.Float(description="Mean Right Ascention"),
        "meandec": fields.Float(description="Mean Declination"),
        "sigmara": fields.Float(
            description="right ascension standard deviation"
        ),
        "sigmadec": fields.Float(description="declination standard deviation"),
        "step_id_corr": fields.String(
            description="correction step pipeline version"
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
        "items": fields.List(fields.Nested(object_list_item)),
    },
)

limit_values_model = Model(
    "Limit Values",
    {
        "min_ndet": fields.Integer(description="Min number of detections"),
        "max_ndet": fields.Integer(description="Max number of detections"),
        "min_firstmjd": fields.Float(description="Min firstmjd"),
        "max_firstmjd": fields.Float(description="Max firstmjd"),
    },
)
