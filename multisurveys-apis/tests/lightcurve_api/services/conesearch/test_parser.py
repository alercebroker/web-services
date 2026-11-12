from db_plugins.db.sql.models_pipeline import Object
from lightcurve_api.models.object import ApiObject
from lightcurve_api.services.conesearch.parser import parse_api_object
from core.idmapper.idmapper import catalog_oid_to_masterid

# Stored oid of ZTF00aaaaaet: the ZTF prefix plus the encoded name (123)
ZTF_OID = int(catalog_oid_to_masterid("ZTF", "ZTF00aaaaaet"))


def test_parse_api_object():
    assert ApiObject(objectId="ZTF00aaaaaet", ra=45.0, dec=45.0, survey_id="ztf") == parse_api_object(
        Object(oid=ZTF_OID, meanra=45.0, meandec=45.0, sid=0)
    )
