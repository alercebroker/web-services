from behave import given, when, then
import sys
from pathlib import Path

PATH = Path(__file__).parent.parent.parent.parent.resolve()

sys.path.append(str(PATH / "examples"))
from simple_app.app import app as s_app
from simple_factory_app import app as sf_app


@given("App is running")
def app_step(context):
    s_app.testing = True
    context.client = s_app.test_client()


@given("App with factory method is running")
def app_factory_step(context):
    sf_app.testing = True
    context.client = sf_app.test_client()


@when("User makes a request")
def user_makes_request_step(context):
    context.response = context.client.get("/")


@then("Request returns without errors")
def request_returns_step(context):
    assert context.response == "Hello World"
