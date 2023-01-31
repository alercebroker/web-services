from functools import wraps
from .get_ralidator import get_ralidator


def set_filters_decorator(filter_list):
    def wrapper_decorator(arg_function):
        @wraps(arg_function)
        async def decorator_function(*args, **kwargs):
            ralidator = get_ralidator(kwargs["request"])
            ralidator.set_app_filters(filter_list)
            return await arg_function(*args, **kwargs)

        return decorator_function

    return wrapper_decorator


def set_permissions_decorator(permissions_list):
    def wrapper_decorator(arg_function):
        @wraps(arg_function)
        async def decorator_function(*args, **kwargs):
            ralidator = get_ralidator(kwargs["request"])
            ralidator.set_required_permissions(permissions_list)
            return await arg_function(*args, **kwargs)

        return decorator_function

    return wrapper_decorator


def check_permissions_decorator(arg_function):
    @wraps(arg_function)
    async def decorator_function(*args, **kwargs):
        ralidator = get_ralidator(kwargs["request"])
        allowed, code = ralidator.check_if_allowed()
        if allowed:
            return await arg_function(*args, **kwargs)
        else:
            # TODO: fix error handling here
            if code == 401:
                return "Expired Token", code
            else:
                return "Forbidden", code

    return decorator_function
