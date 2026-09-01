

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


def get_survey_name(survey_id: int):
    """
    Get the survey name for a given survey ID.

    Parameters
    ----------
    survey_id : int
        The ID of the survey (e.g., 0 for "ztf", 1 for "lsst").

    Returns
    -------
    str
        The survey name.

    Raises
    ------
    ValueError
        If the survey ID is not supported.
    """
    for name, id in SURVEY_IDS.items():
        if id == survey_id:
            return name

    raise ValueError(f"Unsupported survey ID: {survey_id}")