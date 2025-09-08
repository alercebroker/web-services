from typing import List, cast, Callable, ContextManager
from lightcurve_api.services.conesearch.validation import (
    validate_coordinates_params,
    validate_oid_params,
)
from lightcurve_api.models.object import ApiObject
import core.repository.queries.conesearch as queries
from sqlalchemy.orm import Session
from .parser import parsesapi_objects
from toolz.functoolz import pipe
from numpy import int64


def conesearch_coordinates(
    ra: float,
    dec: float,
    radius: float,
    neighbors: int,
    session_factory: Callable[..., ContextManager[Session]],
) -> List[ApiObject]:
    return cast(
        List[ApiObject],
        pipe(
            (ra, dec, radius, neighbors),
            validate_coordinates_params,
            queries.conesearch_coordinates(session_factory),
            parsesapi_objects,
        ),
    )


def conesearch_oid(
    oid: int64,
    radius: float,
    neighbors: int,
    session_factory: Callable[..., ContextManager[Session]],
) -> List[ApiObject]:
    return cast(
        List[ApiObject],
        pipe(
            (oid, radius, neighbors),
            validate_oid_params,
            queries.conesearch_oid(session_factory),
            parsesapi_objects,
        ),
    )
