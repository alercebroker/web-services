Feature: Set permissions to endpoints and block access

  Scenario: Make an authorized request to flask application
    Given a flask application is running
    When an authorized user makes a request to an endpoint that has set permissions
    Then the request returns with code 200


  Scenario: Make an unauthorized request to flask application
    Given a flask application is running
    When an unauthorized user makes a request to an endpoint that has set permissions
    Then the request returns with code 403

