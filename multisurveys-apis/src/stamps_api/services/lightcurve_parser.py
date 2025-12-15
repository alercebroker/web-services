from ..models.lightcurve import detection


def parse_lightcurve(lightcurve_data):
    """
    Parses the magstats data from the database response into a list of MagStat models.

    Args:
        magstats_data (list): List of SQLAlchemy model instances representing magstats.

    Returns:
        list: List of MagStat models.
    """
    parsed_lighturve = []

    for row in lightcurve_data:
        lsst_model_dict = row[0].__dict__.copy()
        detection_model_dict = row[1].__dict__.copy()
        model_parsed = detection(**{
            "mjd": detection_model_dict.get("mjd"),
            "greg": "22/10/2025",
            "measurement_id": lsst_model_dict.get("measurement_id"),
        })
        parsed_lighturve.append(model_parsed)

    return parsed_lighturve
