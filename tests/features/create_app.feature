Feature: Run a flask application that uses Ralidator extension

  Scenario: Run a flask application
    Given: Ralidator is used in an app
    When: User makes a request
    Then: Request returns without errors

  Scenario: Create a flask application using factory method
    Given: Ralidator is used in an app with factory method
    When: User makes a request
    Then: Request returns without errors
