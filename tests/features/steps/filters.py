from behave import given, when, then
import sys
from pathlib import Path
from werkzeug.datastructures import Headers
import jwt
from datetime import datetime, timezone, timedelta

PATH = Path(__file__).parent.parent.parent.parent.resolve()

sys.path.append(str(PATH / "examples"))


@given("a flask application is running")
def app_running(context):
    from filters_app.app import create_app, TEST_SECRET_KEY

    app = create_app()
    app.testing = True
    context.client = app.test_client()
    context.secret_key = TEST_SECRET_KEY


@when('user with filters makes a request to "{endpoint}"')
def request_filters(context, endpoint):
    user_filters = []
    for row in context.table:
        user_filters.append(row["filters"])
    token = {
        "access": "access",
        "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1),
        "jti": "test_jti",
        "user_id": 1,
        "permissions": [],
        "filters": user_filters,
    }
    encripted_token = jwt.encode(token, context.secret_key, algorithm="HS256")
    headers = Headers()
    headers.add("Authorization", "bearer " + encripted_token)
    context.response = context.client.get(endpoint, headers=headers)


@then('the request returns with code "{code}"')
def request_code(context, code):
    code = int(code)
    assert context.response.status_code == code


@then("the response has odd numbers")
def request_filtered(context):
    assert context.response.json == [1, 3, 5, 7, 9]


@then("the response has all numbers")
def original_data(context):
    assert context.response.json == list(range(1, 10))
