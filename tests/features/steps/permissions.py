from behave import given, when, then
import sys
from pathlib import Path
from werkzeug.datastructures import Headers
import jwt
from datetime import datetime, timezone, timedelta

PATH = Path(__file__).parent.parent.parent.parent.resolve()

sys.path.append(str(PATH / "examples"))


@given("a flask application with permissions is running")
def app_running(context):
    from permissions_app.app import create_app, TEST_SECRET_KEY

    app = create_app()
    app.testing = True
    context.client = app.test_client()
    context.secret_key = TEST_SECRET_KEY


@when('authenticated user makes a request to "{endpoint}"')
def request_permissions(context, endpoint):
    user_permissions = []
    for row in context.table:
        user_permissions.append(row["permissions"])
    token = {
        "access": "access",
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
        "jti": "test_jti",
        "user_id": 1,
        "permissions": user_permissions,
        "filters": [],
    }
    encripted_token = jwt.encode(token, context.secret_key, algorithm="HS256")
    headers = Headers()
    headers.add("AUTH_TOKEN", encripted_token)
    context.response = context.client.get(endpoint, headers=headers)


@when('unauthenticated user makes a request to "{endpoint}"')
def request_public(context, endpoint):
    context.response = context.client.get(endpoint)
