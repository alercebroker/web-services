

SURVEY_IDS = {
    "ztf": 0,
    "lsst": 1,
}

def get_survey_id(survey_name: str):
    """
    Get the survey ID for a given survey name.

    Parameters
    ----------
    survey_name : str
        The name of the survey (e.g., "ztf", "lsst").

    Returns
    -------
    int
        The survey ID.

    Raises
    ------
    ValueError
        If the survey name is not supported.
    """
    survey_name = survey_name.lower()
    
    if survey_name not in SURVEY_IDS:
        raise ValueError(f"Unsupported survey: {survey_name}")

    return SURVEY_IDS[survey_name]