import requests

from object_api.services import tns_service
from object_api.services.tns_service import TNS_TIMEOUT, error_data, get_tns


def test_tns_call_sets_a_timeout(mocker):
    post = mocker.patch.object(tns_service.requests, "post", side_effect=requests.ReadTimeout("slow"))

    get_tns(150.1, 2.2)

    assert post.call_args.kwargs["timeout"] == TNS_TIMEOUT


def test_tns_timeout_shows_the_empty_card(mocker):
    mocker.patch.object(tns_service.requests, "post", side_effect=requests.ConnectTimeout("down"))

    assert get_tns(150.1, 2.2) == error_data()
