from ..models.magstats import MagStat
from ..models.lsst_dia_object import LsstDiaObjectSchema


def parse_magstats(magstats_data, survey_id):
    """
    Parses the magstats data from the database response into a list of MagStat models.

    Args:
        magstats_data (list): List of SQLAlchemy model instances representing magstats.

    Returns:
        list: List of MagStat models.
    """
    parsed_magstats = []

    for row in magstats_data:
        model_dict = row[0].__dict__.copy()
        if survey_id == "ztf":
            model_parsed = MagStat(**model_dict)
        elif survey_id == "lsst":
            model_parsed = LsstDiaObjectSchema(**model_dict)

        parsed_magstats.append(model_parsed)

    return parsed_magstats
