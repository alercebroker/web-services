import json

import pytest
from ralidator_core.settings_factory import (
    RalidatorCoreSettingsFactory,
)
from utils.exceptions import BadSettingException


def test_from_dict_correct():
    test_settings_dict = {
        "user_api_url": "test_url.com",
        "user_api_token": "test_token",
        "secret_key": "test_secret_key",
    }
    expected_settings_dict = {
        "user_api_url": "test_url.com",
        "user_api_token": "test_token",
        "secret_key": "test_secret_key",
        "default_user_permisions": ["basic_user"],
        "default_user_filters": ["*"],
    }
    ralidator_settings = RalidatorCoreSettingsFactory.from_dict(
        test_settings_dict
    )
    assert ralidator_settings.settings == expected_settings_dict


def test_from_dict_missing_key():
    test_settings_dict = {"user_api_url": "test_url.com"}

    with pytest.raises(BadSettingException) as e:
        ralidator_settings = RalidatorCoreSettingsFactory.from_dict(
            test_settings_dict
        )

        assert ralidator_settings.missing_setting_errors == ["secret_key"]
        assert ralidator_settings.value_settings_error == []


def test_from_dict_bad_value():
    test_settings_dict = {
        "user_api_url": "test_url.com",
        "user_api_token": 1234,
        "secret_key": "test_secret_key",
    }

    with pytest.raises(BadSettingException) as e:
        ralidator_settings = RalidatorCoreSettingsFactory.from_dict(
            test_settings_dict
        )

        assert ralidator_settings.missing_setting_errors == []
        assert ralidator_settings.value_settings_error == [
            {"key": "user_api_token", "value": int, "expected": str}
        ]


def test_from_json():
    test_settings_dict = {
        "user_api_url": "test_url.com",
        "user_api_token": "test_token",
        "secret_key": "test_secret_key",
    }
    expected_settings_dict = {
        "user_api_url": "test_url.com",
        "user_api_token": "test_token",
        "secret_key": "test_secret_key",
        "default_user_permisions": ["basic_user"],
        "default_user_filters": ["*"],
    }
    test_settings_json = json.dumps(test_settings_dict)
    ralidator_settings = RalidatorCoreSettingsFactory.from_json(
        test_settings_json
    )
    assert ralidator_settings.settings == expected_settings_dict
