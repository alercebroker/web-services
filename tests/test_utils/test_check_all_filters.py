
from package.utils.utils import check_all_filters

TEST_FILTERS_LIST = ["filter1", "filter2", "filter3"]

def test_correct_callbacks_list():
    test_callbacks_dict = {
        "filter1": lambda x: x,
        "filter2": lambda x: x,
        "filter3": lambda x: x
    }
    result = check_all_filters(TEST_FILTERS_LIST, test_callbacks_dict)

    assert result[0]
    assert result[1] == []

def test_missing_callback_key():
    test_callbacks_dict = {
        "filter2": lambda x: x,
    }
    result = check_all_filters(TEST_FILTERS_LIST, test_callbacks_dict)

    assert not result[0]
    assert result[1] == ["Missing filter1", "Missing filter3"]

def test_key_with_invalid_value():
    test_callbacks_dict = {
        "filter1": "a string",
        "filter2": lambda x: x,
        "filter3": 1234
    }

    result = check_all_filters(TEST_FILTERS_LIST, test_callbacks_dict)

    assert not result[0]
    assert result[1] == ["Bad value for filter1", "Bad value for filter2"]