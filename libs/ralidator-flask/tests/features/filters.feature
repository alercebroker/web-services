Feature: Set filters to endpoints and modify the response

  Scenario: Make a request to endpoint with filters
    Given a flask application is running
    When user with filters makes a request to "/filter_even"
      | filters |
      | *       |
    Then the request returns with code "200"
    And the response has odd numbers


  Scenario: Make a request to endpoint with filters but user has other filters
    Given a flask application is running
    When user with filters makes a request to "/filter_even"
      | filters |
      | filterA |
    Then the request returns with code "200"
    And the response has all numbers

  Scenario: Make a request to endpoint with filters but user has no filters
    Given a flask application is running
    When user with filters makes a request to "/no_filters"
      | filters |
    Then the request returns with code "200"
    And the response has all numbers

  Scenario: Make a request to endpoint without filters
    Given a flask application is running
    When user with filters makes a request to "/no_filters"
      | filters |
      | *       |
    Then the request returns with code "200"
    And the response has all numbers
