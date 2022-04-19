from behave import given, when, then


@given("Ralidator is used in an app")
def ralidator_app_step():
    raise NotImplementedError()


@when("User makes a request")
def user_makes_request_step():
    raise NotImplementedError()


@then("Request returns without errors")
def request_returns_step():
    raise NotImplementedError()
