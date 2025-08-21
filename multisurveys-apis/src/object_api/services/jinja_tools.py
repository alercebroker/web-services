import math


def truncate_float(number, decimals=3):
    multiplier = 10**decimals
    return math.trunc(number * multiplier) / multiplier
