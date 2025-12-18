import math
from lightcurve_api.routes.htmx.parsers import ConfigState


def _check_limits_conditions(config_state: ConfigState):
    if config_state.external_sources.enabled == True:
        return False

    return True

def _calculate_approximate_decimal(config_state: ConfigState):
    if config_state.flux:
        return 0

    return 2

def _aproximate_errors(min_error: float, max_error:float, aproximate_decimal: int):
    min_error = math.floor(min_error * (10**aproximate_decimal)) / (10**aproximate_decimal)
    max_error = math.ceil(max_error * (10**aproximate_decimal)) / (10**aproximate_decimal)

    return min_error, max_error