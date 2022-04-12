from package.ralidator_core.ralidator_core import Ralidator
from datetime import datetime, timezone, timedelta
import jwt

TEST_FILTERS = ["filter1", "filter2", "filter3"]
TEST_PERMISIONS = ["permision1", "permision2", "permisoin3"]
TEST_SECRET_KEY = "secret_key"


def test_ralidator_constructor():
    test_callbacks_dict = {
        "filter1": lambda x: x,
        "filter2": lambda x: x
    }

    # exception?
    ralidator = Ralidator(test_callbacks_dict)

def test_authenticate_token_valid():
    test_callbacks_dict = {
        "filter1": lambda x: x,
        "filter2": lambda x: x,
        "filter3": lambda x: x
    }
    token = {
        'token_type': 'access',
        'exp': datetime.now(tz=timezone.utc) + timedelta(hours=1),
        'jti': 'test_jti',
        'user_id': 1,
        "permisions": ["permision1", "permision2"],
        "filters": ["filter1", "filter2"    ]
    }
    encripted_token = jwt.encode(token, TEST_SECRET_KEY, algorithm="HS256")

    ralidator = Ralidator(test_callbacks_dict)
    ralidator.authenticate_token(TEST_SECRET_KEY, encripted_token)
    
    assert ralidator.given_permisions == ["permision1", "permision2"]
    assert ralidator.given_filters == ["filter1", "filter2"]

def test_authenticate_token_invalid():
    test_callbacks_dict = {
        "filter1": lambda x: x,
        "filter2": lambda x: x,
        "filter3": lambda x: x
    }
    # token expired
    token = {
        'token_type': 'access',
        'exp': datetime.now(tz=timezone.utc) + timedelta(hours=-1),
        'jti': 'test_jti',
        'user_id': 1,
        "permisions": ["permision1", "permision2"],
        "filters": ["filter1", "filter2"]
    }
    encripted_token = jwt.encode(token, TEST_SECRET_KEY, algorithm="HS256")


    ralidator = Ralidator(test_callbacks_dict)
    # raise error? return result? set variable to be readed in the future, in check allowed?
    ralidator.authenticate_token(TEST_SECRET_KEY, encripted_token)

def test_authenticate_token_default_token():
    test_callbacks_dict = {
        "filter1": lambda x: x,
        "filter2": lambda x: x,
        "filter3": lambda x: x
    }
    ralidator = Ralidator(test_callbacks_dict)
    ralidator.authenticate_token(TEST_SECRET_KEY, None)
    
    # definir donde y cuales
    assert ralidator.given_permisions == []
    assert ralidator.given_filters == []

def test_check_allowed_allowed():
    test_callbacks_dict = {
        "filter1": lambda x: x,
        "filter2": lambda x: x,
        "filter3": lambda x: x
    }
    token = {
        'token_type': 'access',
        'exp': datetime.now(tz=timezone.utc) + timedelta(hours=1),
        'jti': 'test_jti',
        'user_id': 1,
        "permisions": ["permision1", "permision2"],
        "filters": ["filter1", "filter2"    ]
    }
    encripted_token = jwt.encode(token, TEST_SECRET_KEY, algorithm="HS256")

    ralidator = Ralidator(test_callbacks_dict)
    ralidator.authenticate_token(TEST_SECRET_KEY, encripted_token)
    ralidator.set_required_permisions(["permision1"])
    result = ralidator.check_if_allowed()
    assert result

def test_check_allowed_not_allowed():
    test_callbacks_dict = {
        "filter1": lambda x: x,
        "filter2": lambda x: x,
        "filter3": lambda x: x
    }
    token = {
        'token_type': 'access',
        'exp': datetime.now(tz=timezone.utc) + timedelta(hours=1),
        'jti': 'test_jti',
        'user_id': 1,
        "permisions": ["permision1", "permision2"],
        "filters": ["filter1", "filter2"    ]
    }
    encripted_token = jwt.encode(token, TEST_SECRET_KEY, algorithm="HS256")

    ralidator = Ralidator(test_callbacks_dict)
    ralidator.authenticate_token(TEST_SECRET_KEY, encripted_token)
    ralidator.set_required_permisions(["permision3"])
    result = ralidator.check_if_allowed()
    assert not result

def test_apply_filters():
    # pendiente, una idea es aplicar todos los filtros a un
    # elemnto de la lista, si se queda al final se agrega al
    # resultado si es none tras algun filtro, se pasa al siguiente

    pass