
class Ralidator(object):
    """The ralidator core class manage the permision to resources
    and the filtering of a potential response. It require to be
    instanciated wtith a dictionary of callables wich are related
    to each filter name.

    :param filter_callables: Required and validated dictionary
        that is suposed to map each filter name to a callable defined
        in the service using Ralidator
    :type filter_callables: dict
    """

    def __init__(self, filters_callables) -> None:
        """Constructor method
        """
        raise  NotImplementedError()

    def authenticate_token(self, secret_key, token=None):
        """Decript the token received, then validate the structure of
        result and store the permisions and the filters of the user.
        If no token is used, the autentication will use the default
        user permisions and filters.

        :param secret_key: The secret string that will be used to decript
            the JWT token.
        :type secret_key: str
        :param token: A JWT token string. Its specteded to be the
            auth token included in the http requests. Defaults to none
        :type token: str
        """
        raise  NotImplementedError()

    def set_required_permisions(self, permisions_list):
        """Setter for the required permisions attribute.

        :param permisions_list: The list of permisions to be stored
            in the required_permisions attibute
        :type permisions_list: list
        """
        raise  NotImplementedError()

    def set_given_permisions(self, permisions_list):
        """Setter for the given permisions attibute.

        :param permisions_list: The list of permisions to be stored
            in the given_permisions attibute
        :type permisions_list: list
        """
        raise  NotImplementedError()

    def check_if_allowed(self):
        """Search for at least one of the required_permisions in the
        given_permmisions.

        :return: True if at least one of the required permisions is
            present in the given permisions, false if not.
        :rtype: bool
        """
        raise  NotImplementedError()

    def set_required_filters(self, filters_list):
        """Setter for the required filters.

        :param filters_list: The list of filters to be stored in the
            required_filters attribute.
        :type filters_list: list
        """
        raise  NotImplementedError()

    
    def set_given_filters(self, filters_list):
        """Setter for the given filters.

        :param filters_list: The list of filters to be stored in the
            given_filters attribute.
        :type filters_list: list
        """
        raise  NotImplementedError()
    
    def apply_filters(self, result_value):
        """Search for every filter in given filters that is in required
        filters. It apply every filter found this way to the result.

        :param result_value: the raw return value to be given to the client.
            Some of the values may be removed from result_value after the
            filters are apllied.
        """
        raise  NotImplementedError()
    
    def _apply_filter_atomic(self, filter_list, result_value):
        """It apply all the filters in filter_list to the result value, one
        after the other.

        :param: filter_list: the list of filters names to be applied.
        :type  filters_list: list
        :param result_value: the valur to with the filters must be applied
        """
        raise  NotImplementedError()
