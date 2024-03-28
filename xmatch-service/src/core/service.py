# Description: This file contains the service functions that will be used by the API to interact with the database.
from typing import List
from .query_database import find_objects_by_ipix, Mastercat
from healpy.pixelfunc import ang2vec
from healpy import query_disc
from database.database import ConnectionPool
from scipy.spatial import KDTree
from numpy import deg2rad

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
    radius = deg2rad(radius/3600.0)
    ipix = query_disc(2**14, vec, radius, inclusive=True, nest=True)
    return ipix



def get_oids_from_coordinates(
    ra: float,
    dec: float,
    radius: float,
    pool: ConnectionPool,
    cat: str = "all",
    nneighbor: int = 1,
) -> List[Mastercat]:
    """Return a list of object ids at the given coordinates.
    
    Args:
        ra (float): Right ascension.
        dec (float): Declination.
        radius (float): Radius in arcseconds.

    Returns:
        List[Mastercat]: List of id, ra, dec and catalog.
    """
    ipix = get_ipix_from_coordinates(ra, dec, radius)
    ipix = ipix.tolist()
    objects = find_objects_by_ipix(ipix, pool, cat)
    return get_distance_from_point(objects, ra, dec, radius, nneighbor)

def get_distance_from_point(
    all_points: List[Mastercat],
    ra: float,
    dec: float,
    radius: float,
    nneighbor: int,
) -> List[Mastercat]:
    """Return a list of object ids at the given coordinates.
    
    Args:
        all_points (List[Mastercat]): List of Mastercat objects.
        ra (float): Right ascension.
        dec (float): Declination.
        radius (float): Radius in arcseconds.
        nneighbor (int): Number of neighbors to return.

    Returns:
        List[Mastercat]: List of id, ra, dec and catalog.
    """
    if len(all_points) == 0:
        return []
    points = [(point.ra, point.dec) for point in all_points]
    kdtree = KDTree(points) # TODO: use skycoord for better distance calculation
    indices = kdtree.query_ball_point([ra, dec], radius)
    return [all_points[i] for i in indices[:nneighbor]]

