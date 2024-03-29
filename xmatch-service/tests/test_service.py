from database.database import create_connection
from core.service import get_oids_from_coordinates, Mastercat, get_distance_from_point
from healpy.pixelfunc import ang2pix

def test_get_oids_from_coordinates(init_database):
    pool = create_connection("postgres", "postgres", "localhost", "5432", "postgres")
    assert pool is not None
    with pool.connection() as conn:
        with conn.cursor() as cur:
            query = "insert into mastercat (id, ipix, ra, dec, cat) values (%s, %s, %s, %s, %s)"
            ipixes = [
                ang2pix(2**14, 118, 50, lonlat=True, nest=True),
                ang2pix(2**14, 119,51, lonlat=True, nest=True),
                ang2pix(2**14, 120, 52, lonlat=True, nest=True),
            ]
            ipixes = list(map(int, ipixes))
            cur.execute(query, ("1", ipixes[0], 118, 50, "test"))
            cur.execute(query, ("2", ipixes[1], 119, 51, "test"))
            cur.execute(query, ("3", ipixes[2], 120, 52, "test"))
    result = get_oids_from_coordinates(118, 50, 1, pool)
    assert [r.to_dict()["id"] for r in result] == ["1"]
    result = get_oids_from_coordinates(119, 51, 1, pool)
    assert [r.to_dict()["id"] for r in result] == ["2"]

def test_get_oids_from_coordinates_from_catalog(init_database):
    pool = create_connection("postgres", "postgres", "localhost", "5432", "postgres")
    assert pool is not None
    with pool.connection() as conn:
        with conn.cursor() as cur:
            query = "insert into mastercat (id, ipix, ra, dec, cat) values (%s, %s, %s, %s, %s)"
            ipix = int(ang2pix(2**14, 1.0, 1.0, lonlat=True, nest=True))
            cur.execute(query, ("1", ipix, 1.0, 1.0, "wise"))
            cur.execute(query, ("2", ipix, 1.0, 1.0, "vlass"))
    result = get_oids_from_coordinates(1.0, 1.0, 1, pool, "wise")
    assert [r.to_dict()["id"] for r in result] == ["1"]
    result = get_oids_from_coordinates(1.0, 1.0, 1, pool, "vlass")
    assert [r.to_dict()["id"] for r in result] == ["2"]
    result = get_oids_from_coordinates(1.0, 1.0, 1, pool, "all", 2)
    assert [r.to_dict()["id"] for r in result] == ["1","2"]
    result = get_oids_from_coordinates(1.0, 1.0, 1, pool, nneighbor=2)
    assert [r.to_dict()["id"] for r in result] == ["1","2"]

def test_get_oids_from_coordinates_from_catalog_none_found(init_database):
    pool = create_connection("postgres", "postgres", "localhost", "5432", "postgres")
    assert pool is not None
    with pool.connection() as conn:
        with conn.cursor() as cur:
            query = "insert into mastercat (id, ipix, ra, dec, cat) values (%s, %s, %s, %s, %s)"
            ipix = int(ang2pix(2**14, 1.0, 1.0, lonlat=True, nest=True))
            cur.execute(query, ("1", ipix, 1.0, 1.0, "wise"))
            cur.execute(query, ("2", ipix, 1.0, 1.0, "vlass"))
    result = get_oids_from_coordinates(50, 50, 1, pool, "all", nneighbor=10)
    assert result == []

def test_get_distance_from_point():
    points = [
        Mastercat(id="1", ra=1.0, dec=1.0, cat="test"),
        Mastercat(id="2", ra=1.1, dec=1.1, cat="test"),
        Mastercat(id="3", ra=3.0, dec=3.0, cat="test"),
    ]
    result = get_distance_from_point(points, 1.0, 1.0, 1, 1)
    assert [r.to_dict()["id"] for r in result] == ["1"]
    result = get_distance_from_point(points, 1.0, 1.0, 1, 2)
    assert [r.to_dict()["id"] for r in result] == ["1", "2"]
