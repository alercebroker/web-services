Feature: Ask for a lightcurve data

  Scenario: ask for ztf survey data
    Given the databases have ztf and altas alers
    When request lightcurve for an object in ztf survey
    Then the request should return data from ztf

  Scenario: ask for atlas survey data
    Given the databases have ztf and altas alers
    When request lightcurve for an object in atlas survey
    Then the request should return data from ztf

  Scenario: ask for non stored object
    Given the databases have ztf alets
    When request lightcurve for an object in atlas survey
    Then the request should return 404 error