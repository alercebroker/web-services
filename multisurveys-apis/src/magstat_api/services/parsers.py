from ..models.magstats import MagStat
from ..models.lsst_dia_object import LsstDiaObjectSchema


def parse_magstats(magstats_data):
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
        model_parsed = MagStat(**model_dict)
        parsed_magstats.append(model_parsed)

    return parsed_magstats

def parse_lsst_dia_objects(lsst_data):
    """
    Parses the LSST DiaObject data from the database response into a list of LsstDiaObjectSchema models.

    Args:
        lsst_data (list): List of SQLAlchemy model instances representing LSST DiaObjects.

    Returns:
        list: List of LsstDiaObjectSchema models.
    """
    parsed_objects = []

    for row in lsst_data:
        model_dict = row[0].__dict__.copy()
        model_parsed = LsstDiaObjectSchema(**model_dict)
        parsed_objects.append(model_parsed)

    return parsed_objects
