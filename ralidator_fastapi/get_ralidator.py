from ralidator_core.ralidator_core import Ralidator
from starlette.requests import Request


def get_ralidator(request: Request) -> Ralidator:
    return request.state.ralidator
