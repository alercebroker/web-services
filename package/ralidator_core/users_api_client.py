from telnetlib import STATUS
import requests


class UsersApiClient():
    """The client encapsulates the requests to the users api in a
    centralized class.
    """

    def __init__(self, base_url, auth_token) -> None:
        """Constructor method.

        :param base_url: the base url of the users api
        :type base_url: str
        :param auth_token: a basic token used to authenticate
            the ralidator requests in the users api
        :type auth_token: str
        """
        self.base_url = base_url
        self.auth_token = auth_token

    def get_all_filters(self):
        """Makes a request to the users api to get all the filters
        defined in the service.
        Expepct a json response with the filters list:
        {'filters': []}

        :return: Returns a list of strings, that represent all the
        filters in the user api.
        :rtype: list
        """
        request_url = f"{self.base_url}"
        request_header = {
            'Authorization': f"bearer {self.auth_token}"
        }
        response = requests.get(request_url, request_header)

        if response.status_code == 200:
            filters = response.json().get("filters")
            if filters:
                return filters
            else:
                return None
        elif response.status_code == 403:
            return None
        elif response.status_code == 500:
            return None
        else:
            return None
