from psycopg_pool import ConnectionPool
from typing import List

def find_objects_by_ipix(ipix: List[int], db_pool: ConnectionPool, catalog: str = "all"):
    """Return a list of object ids at the given coordinates."""
    with db_pool.connection() as conn:
        with conn.cursor() as cur:
            if catalog == "all":
                query = "SELECT * FROM mastercat WHERE ipix IN ({})".format(",".join(["%s"] * len(ipix)))
                cur.execute(query, ipix)
            else:
                query = "SELECT * FROM mastercat WHERE ipix IN ({}) AND cat = %s".format(",".join(["%s"] * len(ipix)))
                cur.execute(query, ipix + [catalog])
            return [row[0] for row in cur.fetchall()]

def find_objects_in_catalog_by_oid(oid: List[str], catalog: str, pool: ConnectionPool):
    """Return the contents of the catalog for a given object ID."""
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {catalog} WHERE oid = %s", oid)
            return cur.fetchone()
