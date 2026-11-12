"""idmapper encodes ZTF names only. Other surveys' oids are stored as they come."""

import pytest

from core.idmapper.idmapper import catalog_oid_to_masterid, decode_masterid

# Same pair as the pipeline's idmapper tests: the encoding must not change, or stored ZTF oids stop matching.
ZTF_NAME = "ZTF17aaaaauj"
ZTF_OID = 36028933559737489


def test_ztf_name_encoding_is_unchanged():
    assert catalog_oid_to_masterid("ZTF", ZTF_NAME, validate=True) == ZTF_OID
    assert decode_masterid(ZTF_OID) == ("ZTF", ZTF_NAME)


@pytest.mark.parametrize("catalog", ["LSST", "ATLAS", "LS4"])
def test_other_catalogs_are_rejected(catalog):
    with pytest.raises(ValueError, match="Only ZTF names are encoded"):
        catalog_oid_to_masterid(catalog, "170591527609303944")
