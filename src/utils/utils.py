import jwt
from returns.result import Success, Failure


def decript_and_parse(token, secret_key):
    """Decript the token using the key secret string. The result should
    be a dictionary and the keys will be validated. Beside the auth fields
    of the token, ralidator expects the permissions and filters fields.

    :param token: A JWT string with authentication data for the user.
    :type token: str
    :param key: The secret key used to decript the auth token in the users
    api, used here to decript the token.
    :type key: str
    :return: Result, if sucess returns the dict with the auth data.
    :rtype: Result
    """

    try:
        decripted_token = jwt.decode(
            token,
            secret_key,
            algorithms=["HS256"],
            options={
                "require": [
                    "access",
                    "exp",
                    "jti",
                    "user_id",
                    "permissions",
                    "filters",
                ]
            },
        )
        if isinstance(decripted_token["permissions"], list) and isinstance(
            decripted_token["filters"], list
        ):
            return Success(decripted_token)
        else:
            return Failure(Exception("Bad permission or filter value"))
    except Exception as e:
        return Failure(e)


def check_all_filters(filters_list, callbacks_map):
    """Check if every element of the filters list has a key in the dict
    callabacks_map, and that the value for that key is a callable.

    :param filters_list: a list of string, it represent the filters
        in the roles system.
    :type filters_list: list
    :param callbacks_map: a dictionary of callables, the key should be
        the name of a filter and the value a callable.
    :type callbacks_map: dict
    :return: a 2 tuple, the first element is a boolean that represent if
        the callbacks_map was correct or not, the seccond element is a dict
        of errors found, if any.
    :rtype: tuple. boolean, dict
    """
    missing_filters = []
    bad_values = []
    for filter in filters_list:
        if filter in callbacks_map:
            if not callable(callbacks_map[filter]):
                bad_values.append(filter)
        else:
            missing_filters.append(filter)

    if len(missing_filters) == 0 and len(bad_values) == 0:
        return True, None
    else:
        errors_dict = {
            "missing_filter": missing_filters,
            "bad_values": bad_values,
        }
        return False, errors_dict
