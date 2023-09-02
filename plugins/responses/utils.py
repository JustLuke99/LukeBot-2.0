from datetime import datetime

from .contants import ZKRATKY


# TODO předelat
def delay_check(key):
    time_difference = (datetime.utcnow() - ZKRATKY[key]["tmp"]).total_seconds()
    if time_difference < ZKRATKY[key]["delay"]:
        return True
    ZKRATKY[key]["tmp"] = datetime.utcnow()
