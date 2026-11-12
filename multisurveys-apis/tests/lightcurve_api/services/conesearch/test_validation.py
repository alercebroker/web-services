import pytest

from lightcurve_api.services.conesearch.validation import (
    validate_coordinates_params,
    validate_oid_params,
)


def test_validate_coordinates_params():
    params = [
        (45.0, 45.0, 30.0, 10),
        (0, 0, 30.0, 10),
        (0, 0, 30, -1),
        (-1, 0, 30, 1),
        (360, -200, 30, 1),
        (360, 90, 0, 1),
    ]
    expected = [
        (45.0, 45.0, 30.0, 10),
        (0, 0, 30.0, 10),
        "Neighbors must be greater than 0",
        "RA must be greater than 0 and lower than 360",
        "Dec must be greater than -90 and lower than 90",
        "Radius must be greater than 0",
    ]
    for param, exp in zip(params, expected):
        try:
            assert exp == validate_coordinates_params(param)
        except ValueError as e:
            assert str(e) == exp


def test_validate_oid_params():
    validate_oid_params(radius=30.0, neighbors=10)  # valid: no error


@pytest.mark.parametrize(
    "radius, neighbors, message",
    [
        (30.0, 0, "Neighbors must be greater than 0"),
        (-30, 1, "Radius must be greater than 0"),
    ],
)
def test_validate_oid_params_rejects(radius, neighbors, message):
    with pytest.raises(ValueError, match=message):
        validate_oid_params(radius=radius, neighbors=neighbors)
