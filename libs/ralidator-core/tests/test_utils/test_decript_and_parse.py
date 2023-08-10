import jwt
from datetime import datetime, timedelta, timezone
from returns.pipeline import is_successful
from utils.utils import decript_and_parse


TEST_SECRET_KEY = "secret_key"


def generate_valid_token(timestap_time=False, remove_keys=[]):
    token = {
        "access": "access",
        "exp": int(
            (datetime.now(tz=timezone.utc) + timedelta(hours=1)).timestamp()
        ),
        "jti": "test_jti",
        "user_id": 1,
        "permissions": ["permission1", "permission2"],
        "filters": ["filter1", "filter2"],
    }
    for key in remove_keys:
        token.pop(key)
    return token


def test_decript_correct_token():
    test_token = generate_valid_token()
    assert_token = generate_valid_token(timestap_time=True)
    encripted_test_token = jwt.encode(
        test_token, TEST_SECRET_KEY, algorithm="HS256"
    )
    result = decript_and_parse(encripted_test_token, TEST_SECRET_KEY)

    assert is_successful(result)
    assert result.unwrap() == assert_token

    test_token = generate_valid_token()
    test_token["permissions"] = []
    test_token["filters"] = []
    assert_token = generate_valid_token(timestap_time=True)
    assert_token["permissions"] = []
    assert_token["filters"] = []
    encripted_test_token = jwt.encode(
        test_token, TEST_SECRET_KEY, algorithm="HS256"
    )
    result = decript_and_parse(encripted_test_token, TEST_SECRET_KEY)

    assert is_successful(result)
    assert result.unwrap() == assert_token


def test_decript_bad_token():
    encripted_test_token = (
        "eyJ0eXAiOiIGJbnQgdGhhdCB0aGUgand0IHdvcmtzIn0._zMfzK5Ay-4ymIop6mqe8"
    )
    result = decript_and_parse(encripted_test_token, TEST_SECRET_KEY)

    assert not is_successful(result)


def test_decipt_invalid_token():
    # expired
    test_token = generate_valid_token()
    test_token["exp"] = datetime.now(tz=timezone.utc) + timedelta(hours=-1)
    encripted_test_token = jwt.encode(
        test_token, TEST_SECRET_KEY, algorithm="HS256"
    )
    result = decript_and_parse(encripted_test_token, TEST_SECRET_KEY)

    assert not is_successful(result)

    # missing attributes
    test_token = generate_valid_token(remove_keys=["access"])
    encripted_test_token = jwt.encode(
        test_token, TEST_SECRET_KEY, algorithm="HS256"
    )
    result = decript_and_parse(encripted_test_token, TEST_SECRET_KEY)

    assert not is_successful(result)

    test_token = generate_valid_token(remove_keys=["exp"])
    encripted_test_token = jwt.encode(
        test_token, TEST_SECRET_KEY, algorithm="HS256"
    )
    result = decript_and_parse(encripted_test_token, TEST_SECRET_KEY)

    assert not is_successful(result)

    test_token = generate_valid_token(remove_keys=["jti"])
    encripted_test_token = jwt.encode(
        test_token, TEST_SECRET_KEY, algorithm="HS256"
    )
    result = decript_and_parse(encripted_test_token, TEST_SECRET_KEY)

    assert not is_successful(result)

    test_token = generate_valid_token(remove_keys=["user_id"])
    encripted_test_token = jwt.encode(
        test_token, TEST_SECRET_KEY, algorithm="HS256"
    )
    result = decript_and_parse(encripted_test_token, TEST_SECRET_KEY)

    assert not is_successful(result)

    test_token = generate_valid_token(remove_keys=["permissions"])
    encripted_test_token = jwt.encode(
        test_token, TEST_SECRET_KEY, algorithm="HS256"
    )
    result = decript_and_parse(encripted_test_token, TEST_SECRET_KEY)

    assert not is_successful(result)

    test_token = generate_valid_token(remove_keys=["filters"])
    encripted_test_token = jwt.encode(
        test_token, TEST_SECRET_KEY, algorithm="HS256"
    )
    result = decript_and_parse(encripted_test_token, TEST_SECRET_KEY)

    assert not is_successful(result)

    # bad permissions and filters values

    test_token = generate_valid_token()
    test_token["permissions"] = "bad value"
    encripted_test_token = jwt.encode(
        test_token, TEST_SECRET_KEY, algorithm="HS256"
    )
    result = decript_and_parse(encripted_test_token, TEST_SECRET_KEY)

    assert not is_successful(result)

    test_token = generate_valid_token()
    test_token["filters"] = "bad value"
    encripted_test_token = jwt.encode(
        test_token, TEST_SECRET_KEY, algorithm="HS256"
    )
    result = decript_and_parse(encripted_test_token, TEST_SECRET_KEY)

    assert not is_successful(result)
