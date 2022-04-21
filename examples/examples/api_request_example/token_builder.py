import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "a_secret_key" # from text/config.yml

def build_admin_token():
    token = {
        "token_type": "access",
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
        "jti": "test_jti",
        "user_id": 1,
        "permissions": ["admin"],
        "filters": [],
    }
    encripted_token = jwt.encode(token, SECRET_KEY, algorithm="HS256")
    return encripted_token
