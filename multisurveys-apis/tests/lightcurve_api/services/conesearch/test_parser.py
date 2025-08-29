from db_plugins.db.sql.models import Object
from lightcurve_api.models.object import ApiObject
from lightcurve_api.services.conesearch.parser import parse_api_object


def test_parse_api_object():
    assert ApiObject(
        objectId="ZTF00aaaaaet", ra=45.0, dec=45.0
    ) == parse_api_object(Object(oid=123, meanra=45.0, meandec=45.0))
