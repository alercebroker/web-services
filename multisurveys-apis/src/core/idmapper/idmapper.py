import numpy as np

from .survey_mapper import DEFAULT_SURVEY, SURVEY_IDS, get_survey_id
from .ztf import encode_ztf_to_masterid_without_survey, decode_masterid_for_ztf

# Only ZTF names are encoded. Objects are keyed by (oid, sid) and an oid is unique only within its
# survey, so other surveys' oids are stored as they come (see parse_oid).
# A ZTF oid is the encoded ZTF name with a prefix in its top 8 bits. The prefix is sid + 1, so every
# stored ZTF oid has prefix 1. Same rule as the pipeline's idmapper (libs/idmapper/idmapper/mapper.py).
PREFIX_SHIFT = 63 - 8
ZTF_PREFIX = SURVEY_IDS["ztf"] + 1
MAX_OID = 2**63 - 1
MAX_OIDS_PER_REQUEST = 200


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
    if survey not in OID_PARSERS:
        raise ValueError(f"Unsupported survey: {survey}")
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
    Convert a ZTF object name to a master ID.

    Parameters
    ----------
    catalog : str
        The name of the catalog. Only "ZTF" is supported.
    catalog_oid : str
        The ZTF object name, e.g. "ZTF18aarwvbm".
    validate: bool
        If True, validate the ZTF name before conversion.
    Returns
    -------
    np.int64
        The master ID.
    """
    if catalog.upper() != "ZTF":
        raise ValueError(f"Unsupported catalog: {catalog}. Only ZTF names are encoded.")

    payload = encode_ztf_to_masterid_without_survey(str(catalog_oid), validate)
    return np.int64((ZTF_PREFIX << PREFIX_SHIFT) + int(payload))


def decode_masterid(masterid: int | np.integer) -> tuple[str, str]:
    """
    Convert a ZTF oid back to ("ZTF", ZTF object name).

    Raises ValueError if the oid doesn't carry the ZTF prefix, so another survey's oid is never
    decoded into a made-up ZTF name.
    """
    masterid = int(masterid)
    prefix = masterid >> PREFIX_SHIFT
    if prefix != ZTF_PREFIX:
        raise ValueError(f"{masterid} is not a ZTF oid: prefix {prefix}, expected {ZTF_PREFIX}.")
    payload = masterid & ((1 << PREFIX_SHIFT) - 1)
    return "ZTF", decode_masterid_for_ztf(np.int64(payload))
