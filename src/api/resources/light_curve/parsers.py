from flask_restx import reqparse

SURVEY_ID_CHOICES = ["ztf", "atlas"]

filters = reqparse.RequestParser()
filters.add_argument(
    "survey_id",
    type=str,
    location="args",
    help="Survey identifier",
    choices=SURVEY_ID_CHOICES,
)


pagination = reqparse.RequestParser()
pagination.add_argument(
    "page",
    type=int,
    location="args",
    help="Result page to retrieve",
)
pagination.add_argument(
    "page_size",
    type=int,
    location="args",
    help="Number of results per page",
)

order = reqparse.RequestParser()
order.add_argument(
    "order_by",
    type=str,
    location="args",
    choices=["mjd"],
    help="Column used for ordering results",
)
order.add_argument(
    "order_mode",
    type=str,
    location="args",
    choices=["ASC", "DESC"],
    help="Ordering direction",
)
