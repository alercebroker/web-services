
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
        result and store the permissions and the filters of the user.
        If no token is used, the autentication will use the default
        user permissions and filters.

        :param secret_key: The secret string that will be used to decript
            the JWT token.
        :type secret_key: str
        :param token: A JWT token string. Its specteded to be the
            auth token included in the http requests. Defaults to none
        :type token: str
        """
        raise  NotImplementedError()

    def set_required_permissions(self, permissions_list):
        """Setter for the required permissions attribute.

        :param permissions_list: The list of permissions to be stored
            in the required_permissions attibute
        :type permissions_list: list
        """
        raise  NotImplementedError()

    def set_given_permissions(self, permissions_list):
        """Setter for the given permissions attibute.

        :param permissions_list: The list of permissions to be stored
            in the given_permissions attibute
        :type permissions_list: list
        """
        raise  NotImplementedError()

    def check_if_allowed(self):
        """Search for at least one of the required_permissions in the
        given_permmisions.

        :return: True if at least one of the required permissions is
            present in the given permissions, false if not.
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
