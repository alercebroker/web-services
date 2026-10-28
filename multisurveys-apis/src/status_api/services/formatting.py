import re
from datetime import UTC, datetime

_DURATION = re.compile(r"(\d+)([smhdwy])")
_UNIT_SECONDS = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800, "y": 31536000}


def duration_seconds(text: str) -> float | None:
    """Seconds in a Prometheus duration ("1h", "15d", "1d12h"). None if there is none."""
    parts = _DURATION.findall(text or "")
    if not parts:
        return None
    return sum(int(n) * _UNIT_SECONDS[u] for n, u in parts)


def human_duration(seconds: float) -> str:
    """86400*2 -> "2 days", 3600 -> "1 hour"."""
    for unit, size in (("day", 86400), ("hour", 3600), ("minute", 60)):
        if seconds >= size and seconds % size == 0:
            n = int(seconds // size)
            return f"{n} {unit}{'s' if n != 1 else ''}"
    return f"{int(seconds)} seconds"


def short_duration(seconds: float) -> str:
    """86400*5 -> "5d", 5400 -> "90m"."""
    for unit, size in (("d", 86400), ("h", 3600), ("m", 60)):
        if seconds >= size and seconds % size == 0:
            return f"{int(seconds // size)}{unit}"
    return f"{int(seconds)}s"


def iso(ts: float | None) -> str | None:
    return None if ts is None else datetime.fromtimestamp(ts, tz=UTC).isoformat(timespec="seconds")
