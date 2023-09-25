from core.service import get_magstats
from api.result_handler import handle_error
from fastapi import HTTPException
import pytest
import unittest



def test_get_ztf_magstats(psql_service, psql_session, init_psql):
    result = get_magstats(
        session_factory=psql_session,
        oid="oid1",
    )
    assert result[0].fid == 123

def test_get_magstats_from_unknown_oid(
    psql_service, psql_session, init_psql
):
    with pytest.raises(HTTPException) as exc:
        get_magstats(
            session_factory=psql_session,
            oid="unknown",
            handle_error=handle_error,
        )

    assert exc.value.status_code == 400
    assert exc.value.detail == "Can't retrieve magstats oid not recognized unknown"


class TestGetMagstatsSQL(unittest.TestCase):

    def test_db_exception(self):

        def mock_session_factory_with_exception():
            raise Exception("Test exception")
        
        with pytest.raises(HTTPException) as exc:
            get_magstats(
                session_factory=mock_session_factory_with_exception,
                oid="oid1",
                handle_error=handle_error,
            )

        assert exc.value.status_code == 500






