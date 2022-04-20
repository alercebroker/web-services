from unittest import result
from returns.pipeline import is_successful
from src.utils.utils import decript_and_parse
from src.utils.exceptions import (
    MissingFilterException,
    FilterExecutionException,
)
from src.ralidator_core.settings_factory import RalidatorCoreSettingsFactory


class Ralidator(object):
    """The ralidator core class manage the permission to resources
    and the filtering of a potential response. It require to be
    instanciated wtith a dictionary of callables wich are related
    to each filter name and a settings dict.

    A filter must be a function that receive a single argument, and
    returns true if the element is fine to be in the response and
    false if not.
    """

    def __init__(
        self, settings: RalidatorCoreSettingsFactory, filters_callables
    ) -> None:
        """Constructor method

        :param settings: a dictionary with the configuration variables
            for the difent services used by ralidator
        :type settings: RalidatorCoreSettingsFactory
        :param filter_callables: Required and validated dictionary
            that is suposed to map each filter name to a callable defined
            in the service using Ralidator
        :type filter_callables: dict
        """
        self.settings = settings
        self.filters_callable = filters_callables
        self.required_permissions = []
        self.app_filters = []

    def authenticate_token(self, token=None):
        """Decript the token received, then validate the structure of
        result and store the permissions and the filters of the user.
        If no token is used, the autentication will use the default
        user permissions and filters.

        :param token: A JWT token string. Its specteded to be the
            auth token included in the http requests. Defaults to none
        :type token: str
        """
        if token:
            auth_dict_result = decript_and_parse(
                token, self.settings.settings.get("secret_key")
            )
            if is_successful(auth_dict_result):
                self.valid_token = True
                auth_dict = auth_dict_result.unwrap()
                self.set_user_permissions(auth_dict["permissions"])
                self.set_user_filters(auth_dict["filters"])
            else:
                # error handler insertado?
                self.valid_token = False
        else:
            self.valid_token = True
            # set default values

    def set_required_permissions(self, permissions_list):
        """Setter for the required permissions attribute.

        :param permissions_list: The list of permissions to be stored
            in the required_permissions attibute
        :type permissions_list: list
        """
        self.required_permissions = permissions_list

    def set_user_permissions(self, permissions_list):
        """Setter for the given permissions attibute.


        :param permissions_list: The list of permissions to be stored
            in the given_permissions attibute
        :type permissions_list: list
        """
        self.user_permissions = permissions_list

    def check_if_allowed(self):
        """Search for at least one of the required_permissions in the
        given_permmisions.

        :return: True if at least one of the required permissions is
            present in the given permissions, false if not.
        :rtype: bool
        """
        if not self.valid_token:
            return False

        if self.required_permissions == []:
            return True

        for permission in self.required_permissions:
            if permission in self.user_permissions:
                return True

        return False

    def set_user_filters(self, filters_list):
        """Setter for the user's filters.

        :param filters_list: The list of filters to be stored in the
            user_filters attribute.
        :type filters_list: list
        """
        self.user_filters = filters_list

    def set_app_filters(self, filters_list):
        """Setter for the application defined filters.

        :param filters_list: The list of filters to be stored in the
            given_filters attribute.
        :type filters_list: list
        """
        self.app_filters = filters_list

    def apply_filters(self, result_value):
        """Search for every filter in given filters that is in required
        filters. It apply every filter found this way to the result.

        :param result_value: the raw return value to be given to the client.
            Some of the values may be removed from result_value after the
            filters are apllied.
        :raise MissingFilterException: If the function wants to apply a filter
            either missing in the callables map or with an incorrect value.
        :raise FilterExecutionException: If for some reason the filter defined failed.
        :return: The filtered result.
        """
        filters_to_apply = []
        missing_filters = []
        
        if self.app_filters == []:
            return result_value

        for filter in self.app_filters:
            if filter in self.user_filters:
                if filter not in self.filters_callable:
                    missing_filters.append(filter)
                filters_to_apply.append(filter)

        if len(missing_filters) > 0:
            raise MissingFilterException(missing_filters)

        if isinstance(result_value, list):
            filtered_result = []
            for ele in result_value:
                if self._apply_filter_atomic(filters_to_apply, ele):
                    filtered_result.append(ele)
            return filtered_result

        else:
            if self._apply_filter_atomic(filters_to_apply, result_value):
                return result_value
            else:
                return None

    def _apply_filter_atomic(self, filter_list, result_value):
        """It apply all the filters in filter_list to the result value, one
        after the other.

        :param: filter_list: the list of filters names to be applied.
        :type  filters_list: list
        :param result_value: the valur to with the filters must be applied.
        :raise FilterExecutionException: If for some reason the filter defined failed.
        :return: True if the value passed all the filters, false if y failed
            any.
        :rtype: bool
        """
        for filter in filter_list:
            try:
                result = self.filters_callable[filter](result_value)
            except Exception as e:
                raise FilterExecutionException(e)
            if not result:
                return False
        return True
