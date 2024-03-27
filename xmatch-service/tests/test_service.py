from database.database import create_connection
from core.service import get_oids_from_coordinates
from healpy.pixelfunc import ang2pix

def test_get_oids_from_coordinates(init_database):
    pool = create_connection("postgres", "postgres", "localhost", "5432", "postgres")
    assert pool is not None
    with pool.connection() as conn:
        with conn.cursor() as cur:
            query = "insert into mastercat (oid, ipix, ra, dec, cat) values (%s, %s, %s, %s, %s)"
            ipixes = [ang2pix(2**14, 118, 50, lonlat=True), ang2pix(2**14, 119,51, lonlat=True), ang2pix(2**14, 120, 52, lonlat=True)]
            ipixes = list(map(int, ipixes))
            cur.execute(query, ("1", ipixes[0], 118, 50, "test"))
            cur.execute(query, ("2", ipixes[1], 119, 51, "test"))
            cur.execute(query, ("3", ipixes[2], 120, 52, "test"))
    result = get_oids_from_coordinates(118, 50, 1, pool)
    assert result == ["1"]
    result = get_oids_from_coordinates(119, 51, 1, pool)
    assert result == ["2"]

def test_get_oids_from_coordinates_from_catalog(init_database):
    pool = create_connection("postgres", "postgres", "localhost", "5432", "postgres")
    assert pool is not None
    with pool.connection() as conn:
        with conn.cursor() as cur:
            query = "insert into mastercat (oid, ipix, ra, dec, cat) values (%s, %s, %s, %s, %s)"
            ipix = int(ang2pix(2**14, 1.0, 1.0, lonlat=True))
            cur.execute(query, ("1", ipix, 1.0, 1.0, "wise"))
            cur.execute(query, ("2", ipix, 1.0, 1.0, "vlass"))
    result = get_oids_from_coordinates(1.0, 1.0, 1, pool, "wise")
    assert result == ["1"]
    result = get_oids_from_coordinates(1.0, 1.0, 1, pool, "vlass")
    assert result == ["2"]
    result = get_oids_from_coordinates(1.0, 1.0, 1, pool, "all")
    assert result == ["1","2"]
    result = get_oids_from_coordinates(1.0, 1.0, 1, pool)
    assert result == ["1","2"]
