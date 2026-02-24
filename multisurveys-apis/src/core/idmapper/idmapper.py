import numpy as np

from .ztf import encode_ztf_to_masterid_without_survey, decode_masterid_for_ztf

# Constants
SURVEY_IDS = {
    "ZTF": 0,
    #"ATLAS": 2,
    "LSST": 1,
    "SSLSST": 2,
    "LS4": 4,
}
SURVEY_PREFIX_LEN_BITS = 8
SURVEY_IDS["MAXSURVEY"] = 2**SURVEY_PREFIX_LEN_BITS - 1

REVERSE_SURVEY_IDS = dict((zip(SURVEY_IDS.values(), SURVEY_IDS.keys())))


def encode_ids(survey, oids):
    encode_array = []
    for id in oids:
        encode_id = catalog_oid_to_masterid(survey.upper(), id)
        encode_array.append(encode_id)

    return encode_array


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
