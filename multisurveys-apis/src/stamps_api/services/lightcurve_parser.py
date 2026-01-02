from ..models.lightcurve import detection


from datetime import datetime, timedelta, timezone

def _mjd_to_date(mjd):
    if mjd is None or mjd == '':
        return None
    
    days_from_epoch = float(mjd) - 40587
    date_obj = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(days=days_from_epoch)
    
    return date_obj.strftime('%a, %d %b %Y %H:%M:%S UT')
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
            "greg": str(_mjd_to_date(detection_model_dict.get("mjd"))),
            "measurement_id": lsst_model_dict.get("measurement_id"),
        })
        parsed_lighturve.append(model_parsed)

    return parsed_lighturve
