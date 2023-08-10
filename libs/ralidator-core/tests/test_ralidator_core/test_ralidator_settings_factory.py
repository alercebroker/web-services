import json

import pytest
from ralidator_core.settings_factory import (
    RalidatorCoreSettingsFactory,
)
from utils.exceptions import BadSettingException


def test_from_dict_correct():
    test_settings_dict = {
        "USER_API_URL": "test_url.com",
        "USER_API_TOKEN": "test_token",
        "SECRET_KEY": "test_secret_key",
    }
    expected_settings_dict = {
        "ON_AUTH_ERROR_DEFAULT_USER": False,
        "USER_API_URL": "test_url.com",
        "USER_API_TOKEN": "test_token",
        "SECRET_KEY": "test_secret_key",
        "DEFAULT_USER_PERMISSIONS": ["basic_user"],
        "DEFAULT_USER_FILTERS": ["*"],
    }
    ralidator_settings = RalidatorCoreSettingsFactory.from_dict(
        test_settings_dict
    )
    assert ralidator_settings.settings == expected_settings_dict


def test_from_dict_missing_key():
    test_settings_dict = {"USER_API_URL": "test_url.com"}

    with pytest.raises(BadSettingException) as e:
        ralidator_settings = RalidatorCoreSettingsFactory.from_dict(
            test_settings_dict
        )

        assert ralidator_settings.missing_setting_errors == ["SECRET_KEY"]
        assert ralidator_settings.value_settings_error == []


def test_from_dict_bad_value():
    test_settings_dict = {
        "USER_API_URL": "test_url.com",
        "USER_API_TOKEN": 1234,
        "SECRET_KEY": "test_secret_key",
    }

    with pytest.raises(BadSettingException) as e:
        ralidator_settings = RalidatorCoreSettingsFactory.from_dict(
            test_settings_dict
        )

        assert ralidator_settings.missing_setting_errors == []
        assert ralidator_settings.value_settings_error == [
            {"key": "USER_API_TOKEN", "value": int, "expected": str}
        ]


def test_from_json():
    test_settings_dict = {
        "USER_API_URL": "test_url.com",
        "USER_API_TOKEN": "test_token",
        "SECRET_KEY": "test_secret_key",
    }
    expected_settings_dict = {
        "ON_AUTH_ERROR_DEFAULT_USER": False,
        "USER_API_URL": "test_url.com",
        "USER_API_TOKEN": "test_token",
        "SECRET_KEY": "test_secret_key",
        "DEFAULT_USER_PERMISSIONS": ["basic_user"],
        "DEFAULT_USER_FILTERS": ["*"],
    }
    test_settings_json = json.dumps(test_settings_dict)
    ralidator_settings = RalidatorCoreSettingsFactory.from_json(
        test_settings_json
    )
    assert ralidator_settings.settings == expected_settings_dict
