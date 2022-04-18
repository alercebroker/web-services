from package.utils.utils import check_all_filters

TEST_FILTERS_LIST = ["filter1", "filter2", "filter3"]


def test_correct_callbacks_list():
    test_callbacks_dict = {
        "filter1": lambda x: x,
        "filter2": lambda x: x,
        "filter3": lambda x: x,
    }
    result = check_all_filters(TEST_FILTERS_LIST, test_callbacks_dict)

    assert result[0]
    assert result[1] == None


def test_missing_callback_key():
    test_callbacks_dict = {
        "filter2": lambda x: x,
    }
    expected_errors = {
        "missing_filter": ["filter1", "filter3"],
        "bad_values": [],
    }
    result = check_all_filters(TEST_FILTERS_LIST, test_callbacks_dict)

    assert not result[0]
    assert result[1] == expected_errors


def test_key_with_invalid_value():
    test_callbacks_dict = {
        "filter1": "a string",
        "filter2": lambda x: x,
        "filter3": 1234,
    }
    expected_errors = {
        "missing_filter": [],
        "bad_values": ["filter1", "filter3"],
    }
    result = check_all_filters(TEST_FILTERS_LIST, test_callbacks_dict)

    assert not result[0]
    assert result[1] == expected_errors
