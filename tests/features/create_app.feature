Feature: Run a flask application that uses Ralidator extension

  Scenario: Run a flask application
    Given App is running
    When User makes a request
    Then Request returns without errors

  Scenario: Run a flask application using factory method
    Given App with factory method is running
    When User makes a request
    Then Request returns without errors
