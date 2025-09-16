from typing import Tuple
from numpy import int64


def validate_coordinates_params(
    args: Tuple[float, float, float, int],
) -> Tuple[float, float, float, int]:
    ra, dec, radius, neighbors = args
    if ra < 0 or ra > 360:
        raise ValueError("RA must be greater than 0 and lower than 360")
    if dec < -90 or dec > 90:
        raise ValueError("Dec must be greater than -90 and lower than 90")
    if radius <= 0:
        raise ValueError("Radius must be greater than 0")
    if neighbors <= 0:
        raise ValueError("Neighbors must be greater than 0")
    return ra, dec, radius, neighbors


def validate_oid_params(
    args: Tuple[int64, float, int],
) -> Tuple[int64, float, int]:
    oid, radius, neighbors = args
    if radius <= 0:
        raise ValueError("Radius must be greater than 0")
    if neighbors <= 0:
        raise ValueError("Neighbors must be greater than 0")
    return oid, radius, neighbors
