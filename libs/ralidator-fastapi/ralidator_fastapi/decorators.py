from functools import wraps
from .get_ralidator import get_ralidator
from fastapi import HTTPException


def set_filters_decorator(filter_list):
    def wrapper_decorator(arg_function):
        @wraps(arg_function)
        def decorator_function(*args, **kwargs):
            ralidator = get_ralidator(kwargs["request"])
            ralidator.set_app_filters(filter_list)
            return arg_function(*args, **kwargs)

        return decorator_function

    return wrapper_decorator


def set_permissions_decorator(permissions_list):
    def wrapper_decorator(arg_function):
        @wraps(arg_function)
        def decorator_function(*args, **kwargs):
            ralidator = get_ralidator(kwargs["request"])
            ralidator.set_required_permissions(permissions_list)
            return arg_function(*args, **kwargs)

        return decorator_function

    return wrapper_decorator


def check_permissions_decorator(arg_function):
    @wraps(arg_function)
    def decorator_function(*args, **kwargs):
        ralidator = get_ralidator(kwargs["request"])
        allowed, code = ralidator.check_if_allowed()
        if allowed:
            return arg_function(*args, **kwargs)
        else:
            if code == 401:
                raise HTTPException(status_code=code, detail="Token expired")
            else:
                raise HTTPException(status_code=code, detail="Forbidden")

    return decorator_function
