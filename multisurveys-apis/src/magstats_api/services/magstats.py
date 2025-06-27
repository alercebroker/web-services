from typing import Callable
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from core.repository.queries.magstats import get_magstats_by_oid
from .parsers import parse_magstats

def get_magstats_by_oid(
        oid,
        session_factory: Callable[..., AbstractContextManager[Session]]
        | None = None,
    ):

    result = get_magstats_by_oid(oid, session_factory=session_factory)
    parsed_result = parse_magstats(result)

    return parsed_result