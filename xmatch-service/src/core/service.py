# Description: This file contains the service functions that will be used by the API to interact with the database.
from typing import List, Literal
from .query_database import find_objects_by_ipix
from healpy.pixelfunc import ang2vec
from healpy import query_disc
from database.database import ConnectionPool

class XmatchResult:
    def __init__(self, oid):
        self.oid = oid


    def to_dict(self) -> dict:
        return {
            'oid': self.oid
        }

    def __repr__(self):
        return f'<XmatchResult oid={self.oid}>'

def get_ipix_from_coordinates(ra: float, dec: float, radius: float) -> List[int]:
    """Return a list of HEALPix pixel indices at the given coordinates.
    
    Args:
        ra (float): Right ascension.
        dec (float): Declination.
        radius (float): Radius in arcseconds.

    Returns:
        List[int]: List of HEALPix pixel indices.
    """
    vec = ang2vec(ra, dec, lonlat=True)
    radius = radius / 3600
    ipix = query_disc(2**14, vec, radius, inclusive=True)
    return ipix



def get_oids_from_coordinates(ra: float, dec: float, radius: float, pool: ConnectionPool, cat: str = "all") -> List[str]:
    """Return a list of object ids at the given coordinates.
    
    Args:
        ra (float): Right ascension.
        dec (float): Declination.
        radius (float): Radius in arcseconds.

    Returns:
        List[str]: List of object ids.
    """
    ipix = get_ipix_from_coordinates(ra, dec, radius)
    ipix = ipix.tolist()
    return find_objects_by_ipix(ipix, pool, cat)

