from datetime import datetime, UTC

from .constants import ZKRATKY


def _now() -> datetime:
    return datetime.now(UTC)


def delay_check(key: str) -> bool:
    """Returns True if less than 'delay' seconds have passed since the last trigger."""
    time_difference = (_now() - ZKRATKY[key]["tmp"]).total_seconds()
    if time_difference < ZKRATKY[key]["delay"]:
        return True
    ZKRATKY[key]["tmp"] = _now()
    return False
