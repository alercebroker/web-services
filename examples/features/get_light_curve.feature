Feature: Ask for a lightcurve data

  Scenario: ask for detections for object from ztf survey data
    Given the databases have ztf and altas alerts
    When request detections endpoint for ZTFobject ZTF1 in ZTF survey
    Then the request should return detections for the object from ztf data

  Scenario: ask for non_detections for object from ztf survey data
    Given the databases have ztf and altas alerts
    When request non_detections endpoint for ZTFobject ZTF1 in ZTF survey
    Then the request should return non detections for the object from ztf data

  Scenario: ask for lightcurve for object from ztf survey data
    Given the databases have ztf and altas alerts
    When request lightcurve endpoint for ZTFobject ZTF1 in ZTF survey
    Then the request should return detections and non detections for the object from ztf data

  Scenario: ask for lightcurve for object from atlas survey data
    Given the databases have ztf and altas alerts
    When request lightcurve endpoint for ZTFobject ZTF1 in ATLAS survey
    Then the request should return detections and non detections for the object from ATLAS data

  Scenario: ask for detections for object from atlas survey data
    Given the databases have ztf and altas alerts
    When request detections endpoint for ZTFobject ZTF1 in ATLAS survey
    Then the request should return detections for the object from atlas data

  Scenario: ask for lightcurve for non stored object
    Given the databases have ztf and altas alerts
    When request lightcurve endpoint for ZTFobject ZTF999 in ZTF survey
    Then the request should return 404 error

  Scenario: ask for detections for non stored object
    Given the databases have ztf and altas alerts
    When request detections endpoint for ZTFobject ZTF999 in ZTF survey
    Then the request should return 404 error

  Scenario: ask for non detections for non stored object
    Given the databases have ztf and altas alerts
    When request non_detections endpoint for ZTFobject ZTF999 in ZTF survey
    Then the request should return 404 error

