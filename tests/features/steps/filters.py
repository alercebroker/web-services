from behave import given, when, then
import sys
from pathlib import Path

PATH = Path(__file__).parent.parent.parent.parent.resolve()

sys.path.append(str(PATH / "examples"))


@given("a flask application is running")
def app_running(context):
    from filters_app.app import create_app

    app = create_app()
    app.testing = True
    context.client = app.test_client()


@when("user with filters makes a request to an endpoint that has set filters")
def request_filters(context):
    context.response = context.client.get("/filtered1")


@then("the request returns with code 200")
def request_200(context):
    assert context.response.status_code == 200


@then("the request has filtered data")
def request_filtered(context):
    print(context.response.text)
    assert context.response.json == [1, 3, 5, 7, 9]
