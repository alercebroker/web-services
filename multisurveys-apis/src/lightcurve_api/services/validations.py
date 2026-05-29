from enum import Enum


class Survey(str, Enum):
    """Survey an object belongs to."""

    ztf = "ztf"  # Zwicky Transient Facility
    lsst = "lsst"  # Vera C. Rubin Observatory / LSST


def survey_validate(survey_id):
    surveys = ["ztf", "lsst"]

    if survey_id not in surveys:
        raise ValueError(f"Invalid survey ID '{survey_id}'. Allowed surveys are: {', '.join(surveys)}")
