from ..models.magstats import MagStat

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