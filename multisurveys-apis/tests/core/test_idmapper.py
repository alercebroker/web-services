"""idmapper encodes ZTF names only. Other surveys' oids are stored as they come."""

import pytest

from core.idmapper.idmapper import ZTF_PREFIX, catalog_oid_to_masterid, decode_masterid, parse_oid
from core.idmapper.survey_mapper import SURVEY_IDS, get_survey_name

# Same pair as the pipeline's idmapper tests: the encoding must not change, or stored ZTF oids stop matching.
ZTF_NAME = "ZTF17aaaaauj"
ZTF_OID = 36028933559737489
LSST_OID = 170591527609303944


def test_survey_ids_match_sid_lut():
    # Same values as the pipeline's idmapper and the database's sid_lut table
    assert SURVEY_IDS == {"ztf": 0, "lsst": 1, "lsst_ss": 2}


def test_ztf_prefix_is_sid_plus_one():
    assert ZTF_PREFIX == SURVEY_IDS["ztf"] + 1 == 1


def test_ztf_name_encoding_is_unchanged():
    assert catalog_oid_to_masterid("ZTF", ZTF_NAME, validate=True) == ZTF_OID
    assert decode_masterid(ZTF_OID) == ("ZTF", ZTF_NAME)


@pytest.mark.parametrize("catalog", ["LSST", "ATLAS", "LS4"])
def test_other_catalogs_are_rejected(catalog):
    with pytest.raises(ValueError, match="Only ZTF names are encoded"):
        catalog_oid_to_masterid(catalog, str(LSST_OID))


def test_decoding_a_non_ztf_oid_raises():
    with pytest.raises(ValueError, match="is not a ZTF oid"):
        decode_masterid(LSST_OID)


def test_lsst_ss_has_a_name_but_no_oid_parser():
    assert get_survey_name(2) == "lsst_ss"
    with pytest.raises(ValueError, match="Unsupported survey"):
        parse_oid("lsst_ss", "1")
