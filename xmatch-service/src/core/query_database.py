from psycopg_pool import ConnectionPool
from typing import List
from pydantic import BaseModel

class Mastercat(BaseModel):
    id: str
    ra: float
    dec: float
    cat: str

    @classmethod
    def from_row(cls, row):
        return cls(id=row[0], ra=row[1], dec=row[2], cat=row[3])

    def to_dict(self):
        return {
            "id": self.id,
            "ra": self.ra,
            "dec": self.dec,
            "cat": self.cat
        }

def find_objects_by_ipix(ipix: List[int], db_pool: ConnectionPool, catalog: str = "all") -> List[Mastercat]:
    """Return a list of object ids at the given coordinates."""
    with db_pool.connection() as conn:
        with conn.cursor() as cur:
            if catalog == "all":
                query = "SELECT id, ra, dec, cat FROM mastercat WHERE ipix IN ({})".format(",".join(["%s"] * len(ipix)))
                cur.execute(query, ipix)
            else:
                query = "SELECT id, ra, dec, cat FROM mastercat WHERE ipix IN ({}) AND cat = %s".format(",".join(["%s"] * len(ipix)))
                cur.execute(query, ipix + [catalog])
            return [Mastercat.from_row(row) for row in cur.fetchall()]

def find_objects_in_catalog_by_oid(oid: List[str], catalog: str, pool: ConnectionPool):
    """Return the contents of the catalog for a given object ID."""
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM {catalog} WHERE oid = %s", oid)
            return cur.fetchone()
