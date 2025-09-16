def survey_validate(survey_id):
    surveys = ["ztf", "lsst"]

    if survey_id not in surveys:
        raise ValueError(f"Invalid survey ID '{survey_id}'. Allowed surveys are: {', '.join(surveys)}")
