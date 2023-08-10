from behave import given, when, then
import sys
from pathlib import Path

PATH = Path(__file__).parent.parent.parent.parent.resolve()

sys.path.append(str(PATH / "examples"))


@given("App is running")
def app_step(context):
    from simple_app.app import app

    app.testing = True
    context.client = app.test_client()


@given("App with factory method is running")
def app_factory_step(context):
    from simple_factory_app.app import create_app

    app = create_app()
    app.testing = True
    context.client = app.test_client()


@when("User makes a request")
def user_makes_request_step(context):
    context.response = context.client.get("/")


@then("Request returns without errors")
def request_returns_step(context):
    assert context.response.status_code == 200
