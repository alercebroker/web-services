from behave import when, given, then

@given("the databases have ztf and altas alers")
def database_setup_ztf_atlas(context):
  raise NotImplemented()

@when("request {endpoint} endpoint for an {object} in {survey_id} survey")
def request_to_endpoint(context, endpoint, object, survey_id):
  raise NotImplemented()

@then("the request should return detections and non detections for the object from {survey_id} data")
def check_lightcurve_response_for_survey(context, survey_id):
  raise NotImplemented()

@then("the request should return detections for the object from {survey_id} data")
def check_detections_response_for_survey(context, survey_id):
  raise NotImplemented()

@then("the request should return non detections for the object from {survey_id} data")
def check_non_detections_response_for_survey(context, survey_id):
  raise NotImplemented()

@then("the request should return {error_code} error")
def check_error_response(context, error_code):
  raise NotImplemented()