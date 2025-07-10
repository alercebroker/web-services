from ..models.probability import Probability

def parse_magstats(probability_data):
    """
    Parses the probability data from the database response into a list of Probability models.

    Args:
        probability_data (list): List of SQLAlchemy model instances representing magstats.

    Returns:
        list: List of Probability models.
    """
    parsed_probability = []
    
    for row in probability_data:
        model_dict = row[0].__dict__.copy()
        model_parsed = Probability(**model_dict)
        parsed_probability.append(model_parsed)

    return parsed_probability