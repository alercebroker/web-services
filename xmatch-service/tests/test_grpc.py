# Description: Test the grpc server
from grpc_server.xmatch_server import XmatchServicer, ConesearchRequest
import pytest
from healpy.pixelfunc import ang2pix

@pytest.mark.usefixtures("init_database", "env_setup")
class TestConesearch():
    def test_conesearch(self):
        server = XmatchServicer()
        with server.pool.connection() as conn:
            with conn.cursor() as cur:
                query = "insert into mastercat (id, ipix, ra, dec, cat) values (%s, %s, %s, %s, %s)"
                ipix = int(ang2pix(2**14, 118.0, -50.0, lonlat=True, nest=True))
                cur.execute(query, ("1", ipix, 118, -50, "wise"))
                cur.execute(query, ("2", ipix, 118, -50, "vlass"))
                cur.execute(query, ("3", ipix, 118, -50, "lsdr10"))
        request = ConesearchRequest(ra=118, dec=-50, radius=1.0, catalog="wise", nneighbors=1)
        response = server.Conesearch(request, None)
        response = response.objects
        assert len(response) == 1
        assert response[0].id == "1"
        assert response[0].ra == 118
        assert response[0].dec == -50
        assert response[0].catalog == "wise"
        assert response[0].distance == 0

    @pytest.mark.skip(reason="Not implemented yet")
    def test_conesearch_with_grcp_client():
        pass
