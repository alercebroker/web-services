Feature: Set permissions to endpoints and block access

  Scenario: Make an authorized request to flask application
    Given a flask application with permissions is running
    When authenticated user makes a request to "/restricted_access"
      | permissions |
      | admin       |
    Then the request returns with code "200"

  Scenario: Make a request without authentication to flask application
    Given a flask application with permissions is running
    When unauthenticated user makes a request to "/restricted_access"
    Then the request returns with code "403"

  Scenario: Make a request without authentication to non restricted endpoint
    Given a flask application with permissions is running
    When unauthenticated user makes a request to "/public_access"
    Then the request returns with code "200"

  Scenario: Make an unauthorized request to flask application
    Given a flask application with permissions is running
    When authenticated user makes a request to "/restricted_access"
      | permissions |
      | common      |
    Then the request returns with code "403"

  Scenario: Make a malformed header request without bearer to flask application
    Given a flask application with permissions is running
    When user makes a request with "no bearer" header
    Then the request returns with code "403"
