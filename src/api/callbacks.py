from asyncio import current_task
from flask import request, g
from time import time
import traceback


def before_request():
    g.time = time()


def after_request(response, logger):
    if request.full_path == "/metrics?":  # pragma: no cover
        return response
    current_time = time()
    elapsed = current_time - g.pop("time", current_time)
    logger.debug(
        "%s %s %s %s %s time:%s seconds",
        request.remote_addr,
        request.method,
        request.scheme,
        request.full_path,
        response.status,
        elapsed,
    )
    return response


def exceptions(e, logger):
    tb = traceback.format_exc()
    logger.error(
        "%s %s %s %s ERROR\n%s",
        request.remote_addr,
        request.method,
        request.scheme,
        request.full_path,
        tb,
    )
    return e.status_code
