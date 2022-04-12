#results? para no usar bools

def decript_and_parse(token, key):
    """Decript the token using the key secret string. The result should
    be a dictionary and the keys will be validated. Beside the auth fields
    of the token, ralidator expects the permisions and filters fields.

    :param token: A JWT string with authentication data for the user.
    :type token: str
    :param key: The secret key used to decript the auth token in the users
    api, used here to decript the token.
    :type key: str
    :return: a 2 tupe, the first element is a boolean that represent if the
        token was valid or not. The seccond is the dict with the user data.
    :rtype: tupe. boolean, dict
    """
    raise NotImplementedError()

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
        the callbacks_map was correct or not, the seccond element is a list
        of error found, if any.
    :rtype: tuple. boolean, list
    """
    raise NotImplementedError()