Feature: Set filters to endpoints and modify the response

  Scenario: Make a request to endpoint with filters
    Given a flask application is running
    When user with filters makes a request to an endpoint that has set filters
    Then the request returns with code 200
    And the request has filtered data

  Scenario: Make a request to endpoint without filters
    Given a flask application is running
    When user with filters makes a request to an endpoint that has not set filters
    Then the request returns with code 200
    And the request has original data

  Scenario: Make a request to endpoint with filters but user has no filters
    Given a flask application is running
    When user without filters makes a request to an endpoint that has filters
    Then the request returns with code 200
    And the request has original data
