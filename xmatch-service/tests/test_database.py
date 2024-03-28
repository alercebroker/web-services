from database.database import create_connection
from core.query_database import find_objects_by_ipix

def test_database(psql_service):
    pool = create_connection("postgres", "postgres", "localhost", "5432", "postgres")
    assert pool is not None
    result = None
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
    assert result == (1,)

def test_find_objects_by_ipix(init_database):
    pool = create_connection("postgres", "postgres", "localhost", "5432", "postgres")
    assert pool is not None
    ipix = [1, 2, 3]
    result = None
    with pool.connection() as conn:
        with conn.cursor() as cur:
            query = "insert into mastercat (id, ipix, ra, dec, cat) values (%s, %s, %s, %s, %s)"
            cur.execute(query, ("1", 1, 1.0, 1.0, "test"))
            cur.execute(query, ("2", 2, 2.0, 2.0, "test"))
            cur.execute(query, ("3", 3, 3.0, 3.0, "test"))
    result = find_objects_by_ipix(ipix, pool)
    result = [r.to_dict() for r in result]
    assert result == [
        {
            "id": "1",
            "ra": 1.0,
            "dec": 1.0,
            "cat": "test"
        },
        {
            "id": "2",
            "ra": 2.0,
            "dec": 2.0,
            "cat": "test"
        },
        {
            "id": "3",
            "ra": 3.0,
            "dec": 3.0,
            "cat": "test"
        }
    ]
