import numpy as np

from .survey_mapper import DEFAULT_SURVEY, get_survey_id
from .ztf import encode_ztf_to_masterid_without_survey, decode_masterid_for_ztf

# Constants
# Prefix of each catalog inside a master id. Not the survey id stored in the database (survey_mapper.SURVEY_IDS).
SURVEY_IDS = {
    "ZTF": 1,
    "ATLAS": 2,
    "LSST": 3,
    "LS4": 4,
}
SURVEY_PREFIX_LEN_BITS = 8
MAX_OID = 2**63 - 1
MAX_OIDS_PER_REQUEST = 200
SURVEY_IDS["MAXSURVEY"] = 2**SURVEY_PREFIX_LEN_BITS - 1

REVERSE_SURVEY_IDS = dict((zip(SURVEY_IDS.values(), SURVEY_IDS.keys())))


def _parse_numeric_oid(text: str) -> int | None:
    if not (text.isascii() and text.isdigit()):
        return None
    if int(text) > MAX_OID:
        raise ValueError(f"Invalid oid '{text}': too large, numeric ids go up to {MAX_OID}.")
    return int(text)


def _parse_ztf_oid(text: str) -> int:
    numeric = _parse_numeric_oid(text)
    if numeric is not None:
        return numeric
    # Raises "Invalid ZTF object ID: ..." for anything that isn't a ZTF name
    return int(catalog_oid_to_masterid("ZTF", text, validate=True))


def _parse_lsst_oid(text: str) -> int:
    numeric = _parse_numeric_oid(text)
    if numeric is not None:
        return numeric
    if text[:3].upper() == "ZTF":
        raise ValueError(f"Invalid oid '{text}': it looks like a ZTF name, but LSST ids are numeric.")
    raise ValueError(f"Invalid oid '{text}': expected a numeric id.")


OID_PARSERS = {
    "ztf": _parse_ztf_oid,
    "lsst": _parse_lsst_oid,
}


def parse_oid(survey: str | None, oid: str | int) -> int:
    """Turn an oid from a request into the multisurvey id stored in the database.

    ZTF takes a numeric id (``36028941599716634``) or a ZTF name (``ZTF18aarwvbm``); LSST takes
    its numeric diaObjectId. Without a survey, the oid is read as ZTF, so queries that didn't
    send one keep working. Raises ValueError for anything else, so routes can answer 400.
    """
    survey = DEFAULT_SURVEY if survey is None else survey.lower()
    get_survey_id(survey)
    return OID_PARSERS[survey](str(oid).strip())


def encode_ids(survey, oids):
    return [parse_oid(survey, oid) for oid in oids]


def decode_ids(items):
    for item in items:
        oid = np.int64(item["oid"])
        _, catalog_oid = decode_masterid(oid)
        item["oid"] = catalog_oid

    return items


def catalog_oid_to_masterid(
    catalog: str,
    catalog_oid: str | np.int64 | int,
    validate: bool = False,
) -> np.int64:
    """
    Convert a catalog object ID to a master ID.

    Parameters
    ----------
    catalog : str
        The name of the catalog (e.g., "ZTF").
    catalog_oid : str
        The ZTF object ID.
    validate: bool
        If True, validate the ztf_oid before conversion.
    Returns
    -------
    str
        The master ID.
    """
    catalog = catalog.upper()
    if catalog not in SURVEY_IDS.keys():
        raise ValueError(f"Unsupported catalog: {catalog}")

    # Add the survey ID to the master ID
    master_id = SURVEY_IDS[catalog] << (63 - SURVEY_PREFIX_LEN_BITS)
    master_id = np.int64(master_id)

    if catalog == "ZTF":
        master_id += encode_ztf_to_masterid_without_survey(str(catalog_oid), validate)
    elif catalog == "LSST":
        return np.int64(catalog_oid)

    return master_id


def decode_masterid(masterid: np.int64) -> tuple[str, str | np.int64]:
    """
    Decode a master ID into its components.

    Parameters
    ----------
    masterid : np.int64
        The master ID.
    Returns
    -------
    tuple[str, str]
        The survey of the object and the original oid.
    """
    # Extract the survey from the master ID
    # survey_id = masterid >> (63 - SURVEY_PREFIX_LEN_BITS)

    masterid_without_survey = np.bitwise_and(masterid, ((1 << (63 - SURVEY_PREFIX_LEN_BITS)) - 1))
    return "ZTF", decode_masterid_for_ztf(masterid_without_survey)
