from core.service import get_magstats
from core.exceptions import OidError
from api.result_handler import handle_error
import pytest


def atest_get_ztf_magstats(psql_service, psql_session, init_psql):
    result = get_magstats(
        session_factory=psql_session,
        oid="oid1",
    )
    assert result[0].fid == 123

def test_get_magstats_from_unknown_oid(
    psql_service, psql_session, init_psql
):
    with pytest.raises(
        OidError, match="Can't retrieve magstats oid not recognized unknown"
    ):
        get_magstats(
            session_factory=psql_session,
            oid="unknown",
            handle_error = handle_error,
        )



