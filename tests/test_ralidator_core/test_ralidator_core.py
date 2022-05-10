import jwt
from ralidator_core.ralidator_core import Ralidator
from ralidator_core.settings_factory import RalidatorCoreSettingsFactory
from datetime import datetime, timezone, timedelta

TEST_FILTERS = ["filter1", "filter2", "filter3"]
TEST_PERMISSIONS = ["permission1", "permission2", "permisoin3"]
TEST_SECRET_KEY = "secret_key"


def test_authenticate_token_valid():
    test_callbacks_dict = {
        "filter1": lambda x: x,
        "filter2": lambda x: x,
        "filter3": lambda x: x,
    }
    token = {
        "token_type": "access",
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
        "jti": "test_jti",
        "user_id": 1,
        "permissions": ["permission1", "permission2"],
        "filters": ["filter1", "filter2"],
    }
    ralidator_settings = RalidatorCoreSettingsFactory()
    ralidator_settings.settings = {"SECRET_KEY": TEST_SECRET_KEY}
    encripted_token = jwt.encode(token, TEST_SECRET_KEY, algorithm="HS256")

    ralidator = Ralidator(ralidator_settings, test_callbacks_dict)
    ralidator.authenticate_token(encripted_token)

    assert ralidator.valid_auth == True
    assert ralidator.user_permissions == ["permission1", "permission2"]
    assert ralidator.user_filters == ["filter1", "filter2"]


def test_authenticate_token_invalid():
    test_callbacks_dict = {
        "filter1": lambda x: x,
        "filter2": lambda x: x,
        "filter3": lambda x: x,
    }
    # token expired
    token = {
        "token_type": "access",
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=-1),
        "jti": "test_jti",
        "user_id": 1,
        "permissions": ["permission1", "permission2"],
        "filters": ["filter1", "filter2"],
    }
    ralidator_settings = RalidatorCoreSettingsFactory()
    ralidator_settings.settings = {"SECRET_KEY": TEST_SECRET_KEY}
    encripted_token = jwt.encode(token, TEST_SECRET_KEY, algorithm="HS256")

    ralidator = Ralidator(ralidator_settings, test_callbacks_dict)
    ralidator.authenticate_token(encripted_token)
    assert ralidator.valid_auth == False
    assert ralidator.auth_error_code == 401

    # token invalid
    token = {
        "token_type": "access",
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
        "jti": "test_jti",
        "user_id": 1,
        "permissions": ["permission1", "permission2"]
    }
    ralidator_settings = RalidatorCoreSettingsFactory()
    ralidator_settings.settings = {"SECRET_KEY": TEST_SECRET_KEY}
    encripted_token = jwt.encode(token, TEST_SECRET_KEY, algorithm="HS256")

    ralidator = Ralidator(ralidator_settings, test_callbacks_dict)
    ralidator.authenticate_token(encripted_token)
    assert ralidator.valid_auth == False
    assert ralidator.auth_error_code == 403


def test_authenticate_token_default_token():
    test_callbacks_dict = {
        "filter1": lambda x: x,
        "filter2": lambda x: x,
        "filter3": lambda x: x,
    }
    ralidator_settings = RalidatorCoreSettingsFactory()
    ralidator_settings.settings = {"SECRET_KEY": TEST_SECRET_KEY}
    ralidator = Ralidator(ralidator_settings, test_callbacks_dict)
    ralidator.authenticate_token(None)

    assert ralidator.valid_auth == True
    assert ralidator.user_permissions == ralidator_settings.settings.get(
        "DEFAULT_USER_PERMISSIONS"
    )
    assert ralidator.user_filters == ralidator_settings.settings.get(
        "default_user_filters"
    )


def test_check_allowed_allowed():
    test_callbacks_dict = {
        "filter1": lambda x: x,
        "filter2": lambda x: x,
        "filter3": lambda x: x,
    }
    token = {
        "token_type": "access",
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
        "jti": "test_jti",
        "user_id": 1,
        "permissions": ["permission1", "permission2"],
        "filters": ["filter1", "filter2"],
    }
    ralidator_settings = RalidatorCoreSettingsFactory()
    ralidator_settings.settings = {"SECRET_KEY": TEST_SECRET_KEY}
    encripted_token = jwt.encode(token, TEST_SECRET_KEY, algorithm="HS256")

    ralidator = Ralidator(ralidator_settings, test_callbacks_dict)
    ralidator.authenticate_token(encripted_token)
    ralidator.set_required_permissions(["permission1"])
    result = ralidator.check_if_allowed()
    assert result == (True, None)


def test_check_allowed_empty_required():
    test_callbacks_dict = {
        "filter1": lambda x: x,
        "filter2": lambda x: x,
        "filter3": lambda x: x,
    }
    token = {
        "token_type": "access",
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
        "jti": "test_jti",
        "user_id": 1,
        "permissions": ["permission1", "permission2"],
        "filters": ["filter1", "filter2"],
    }
    ralidator_settings = RalidatorCoreSettingsFactory()
    ralidator_settings.settings = {"SECRET_KEY": TEST_SECRET_KEY}
    encripted_token = jwt.encode(token, TEST_SECRET_KEY, algorithm="HS256")

    ralidator = Ralidator(ralidator_settings, test_callbacks_dict)
    ralidator.authenticate_token(encripted_token)
    result = ralidator.check_if_allowed()
    assert result == (True, None)


def test_check_allowed_with_bad_token():
    test_callbacks_dict = {
        "filter1": lambda x: x,
        "filter2": lambda x: x,
        "filter3": lambda x: x,
    }
    # not allowed
    token = {
        "token_type": "access",
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
        "jti": "test_jti",
        "user_id": 1
    }
    ralidator_settings = RalidatorCoreSettingsFactory()
    ralidator_settings.settings = {
        "SECRET_KEY": TEST_SECRET_KEY,
        "ON_AUTH_ERROR_DEFAULT_USER": True,
        "DEFAULT_USER_PERMISSIONS": "permission1"
    }
    encripted_token = jwt.encode(token, TEST_SECRET_KEY, algorithm="HS256")

    ralidator = Ralidator(ralidator_settings, test_callbacks_dict)
    ralidator.authenticate_token(encripted_token)
    ralidator.set_required_permissions(["permission1"])
    result = ralidator.check_if_allowed()
    assert result == (True, None)


def test_check_allowed_not_allowed():
    test_callbacks_dict = {
        "filter1": lambda x: x,
        "filter2": lambda x: x,
        "filter3": lambda x: x,
    }
    # not allowed
    token = {
        "token_type": "access",
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
        "jti": "test_jti",
        "user_id": 1,
        "permissions": ["permission1", "permission2"],
        "filters": ["filter1", "filter2"],
    }
    ralidator_settings = RalidatorCoreSettingsFactory()
    ralidator_settings.settings = {"SECRET_KEY": TEST_SECRET_KEY}
    encripted_token = jwt.encode(token, TEST_SECRET_KEY, algorithm="HS256")

    ralidator = Ralidator(ralidator_settings, test_callbacks_dict)
    ralidator.authenticate_token(encripted_token)
    ralidator.set_required_permissions(["permission3"])
    result = ralidator.check_if_allowed()
    assert result == (False, 403)

    # expired
    token = {
        "token_type": "access",
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=-1),
        "jti": "test_jti",
        "user_id": 1,
        "permissions": ["permission1", "permission2"],
        "filters": ["filter1", "filter2"],
    }
    ralidator_settings = RalidatorCoreSettingsFactory()
    ralidator_settings.settings = {"SECRET_KEY": TEST_SECRET_KEY}
    encripted_token = jwt.encode(token, TEST_SECRET_KEY, algorithm="HS256")

    ralidator = Ralidator(ralidator_settings, test_callbacks_dict)
    ralidator.authenticate_token(encripted_token)
    ralidator.set_required_permissions(["permission3"])
    result = ralidator.check_if_allowed()
    assert result == (False, 401)


def test_apply_filters():
    # the test consider the response a list of integers
    test_callbacks_dict = {
        "filter1": lambda x: x > 5,  # allow values over 5
        "filter2": lambda x: x == 7,  # only allow 7
        "filter3": lambda x: x < 10,  # allow values under 10
    }
    test_values = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    token = {
        "token_type": "access",
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
        "jti": "test_jti",
        "user_id": 1,
        "permissions": ["permission1", "permission2"],
        "filters": ["filter1", "filter3"],
    }
    ralidator_settings = RalidatorCoreSettingsFactory()
    ralidator_settings.settings = {"SECRET_KEY": TEST_SECRET_KEY}
    encripted_token = jwt.encode(token, TEST_SECRET_KEY, algorithm="HS256")

    ralidator = Ralidator(ralidator_settings, test_callbacks_dict)
    ralidator.authenticate_token(encripted_token)
    ralidator.set_app_filters(["filter1", "filter2", "filter3"])
    result = ralidator.apply_filters(test_values)
    assert result == [6, 7, 8, 9]

    token = {
        "token_type": "access",
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
        "jti": "test_jti",
        "user_id": 1,
        "permissions": ["permission1", "permission2"],
        "filters": ["filter2"],
    }
    encripted_token = jwt.encode(token, TEST_SECRET_KEY, algorithm="HS256")

    ralidator = Ralidator(ralidator_settings, test_callbacks_dict)
    ralidator.authenticate_token(encripted_token)
    ralidator.set_app_filters(["filter1", "filter2", "filter3"])
    result = ralidator.apply_filters(8)
    assert not result


def test_apply_all_filters():
    # the test consider the response a list of integers
    test_callbacks_dict = {
        "filter1": lambda x: x > 5,  # allow values over 5
        "filter2": lambda x: (x % 2) == 0,  # only allow evens
        "filter3": lambda x: x < 10,  # allow values under 10
    }
    test_values = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    token = {
        "token_type": "access",
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
        "jti": "test_jti",
        "user_id": 1,
        "permissions": ["permission1", "permission2"],
        "filters": ["*"],
    }
    ralidator_settings = RalidatorCoreSettingsFactory()
    ralidator_settings.settings = {"SECRET_KEY": TEST_SECRET_KEY}
    encripted_token = jwt.encode(token, TEST_SECRET_KEY, algorithm="HS256")

    ralidator = Ralidator(ralidator_settings, test_callbacks_dict)
    ralidator.authenticate_token(encripted_token)
    ralidator.set_app_filters(["filter1", "filter2", "filter3"])
    result = ralidator.apply_filters(test_values)
    assert result == [6, 8]
