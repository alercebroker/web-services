from typing import Tuple


# TODO: takes its inputs as one positional tuple so it fits a toolz pipe. That is error-prone: values of the same
# type can be swapped without any error, and the type checker can't catch it. Change it to named parameters, like
# validate_oid_params.
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


def validate_oid_params(*, radius: float, neighbors: int) -> None:
    """Raises ValueError unless the radius and the number of neighbors are positive."""
    if radius <= 0:
        raise ValueError("Radius must be greater than 0")
    if neighbors <= 0:
        raise ValueError("Neighbors must be greater than 0")
