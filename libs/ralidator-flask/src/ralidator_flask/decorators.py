from functools import wraps

from flask import _request_ctx_stack


def set_filters_decorator(filter_list):
    def wrapper_decorator(arg_function):
        @wraps(arg_function)
        def decorator_function(*args, **kwargs):
            ctx = _request_ctx_stack.top
            ctx.ralidator.set_app_filters(filter_list)

            return arg_function(*args, **kwargs)

        return decorator_function

    return wrapper_decorator


def set_permissions_decorator(permissions_list):
    def wrapper_decorator(arg_function):
        @wraps(arg_function)
        def decorator_function(*args, **kwargs):
            ctx = _request_ctx_stack.top
            ctx.ralidator.set_required_permissions(permissions_list)

            return arg_function(*args, **kwargs)

        return decorator_function

    return wrapper_decorator


def check_permissions_decorator(arg_function):
    @wraps(arg_function)
    def decorator_function(*args, **kwargs):
        ctx = _request_ctx_stack.top
        allowed, code = ctx.ralidator.check_if_allowed()
        if allowed:
            return arg_function(*args, **kwargs)
        else:
            if code == 401:
                return "Expired Token", code
            else:
                return "Forbidden", code

    return decorator_function
