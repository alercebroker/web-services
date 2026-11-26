"""The switch for the multisurvey object association tables, shared by the light curve, Aladin and object APIs.

Production doesn't have the tables yet: everything that reads them is off unless ``ASSOCIATION_SCHEMA`` names the
schema that holds them. They are still a test schema, so a failed lookup is logged and only leaves its part of the
page out (``safe_lookup``).
"""

import logging
import os
from typing import Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Read once at import, like every model's schema (core/repository/association_models.py).
ASSOCIATION_SCHEMA = os.getenv("ASSOCIATION_SCHEMA") or None


def association_enabled() -> bool:
    return ASSOCIATION_SCHEMA is not None


def safe_lookup(lookup: Callable[[], T], fallback: T, what: str) -> T:
    """``lookup()``, or ``fallback`` if it fails: the page is shown without what it would have added."""
    try:
        return lookup()
    except Exception:
        logger.warning("Could not read %s", what, exc_info=True)
        return fallback
