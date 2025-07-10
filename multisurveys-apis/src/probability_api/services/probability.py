from typing import Callable
from contextlib import AbstractContextManager
from sqlalchemy.orm import Session
from core.repository.queries.probability import get_probability_by_oid
from .parsers import parse_probability

def get_probability(
        oid,
        classifier: str | None = None,
        session_factory: Callable[..., AbstractContextManager[Session]]
        | None = None,
    ):

    result = get_probability_by_oid(oid, classifier, session_factory=session_factory)
    parsed_result = parse_probability(result)

    return parsed_result