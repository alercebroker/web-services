Feature: Ask for a lightcurve data

  Scenario: ask for lightcurve for object from ztf survey data
    Given the databases have ztf and altas alers
    When request lightcurve endpoint for an ZTFobject in ZTF survey
    Then the request should return detections and non detections for the object from ztf data

  Scenario: ask for detections for object from ztf survey data
    Given the databases have ztf and altas alers
    When request detections endpoint for an ZTFobject in ZTF survey
    Then the request should return detections for the object from ztf data

  Scenario: ask for non_detections for object from ztf survey data
    Given the databases have ztf and altas alers
    When request non_detections endpoint for an ZTFobject in ZTF survey
    Then the request should return non detections for the object from ztf data

  Scenario: ask for lightcurve for object from atlas survey data
    Given the databases have ztf and altas alers
    When request lightcurve endpoint for an ATLASobject in ATLAS survey
    Then the request should return detections and non detections for the object from ATLAS data

  Scenario: ask for detections for object from atlas survey data
    Given the databases have ztf and altas alers
    When request detections endpoint for an ATLASobject in ATLAS survey
    Then the request should return detections for the object from atlas data

  Scenario: ask for non_detections for object from atlas survey data
    Given the databases have ztf and altas alers
    When request non_detections endpoint for an ATLASobject in ATLAS survey
    Then the request should return non detections for the object from atlas data

  Scenario: ask for lightcurve for non stored object
    Given the databases have ztf and altas alers
    When request lightcurve endpoint for an ATLASobject in ZTF survey
    Then the request should return 404 error

  Scenario: ask for detections for non stored object
    Given the databases have ztf and altas alers
    When request detections endpoint for an ATLASobject in ZTF survey
    Then the request should return 404 error

  Scenario: ask for non detections for non stored object
    Given the databases have ztf and altas alers
    When request non_detections endpoint for an ATLASobject in ZTF survey
    Then the request should return 404 error

  Scenario: ask for lightcurve for an object with no survey specified
    Given the databases have ztf and altas alers
    When request lightcurve endpoint for an ZTFobject in NO survey
    Then the request should return 400 error

  Scenario: ask for detections for an object with no survey specified
    Given the databases have ztf and altas alers
    When request detections endpoint for an ZTFobject in NO survey
    Then the request should return 400 error

  Scenario: ask for non_detections for an object with no survey specified
    Given the databases have ztf and altas alers
    When request non_detections endpoint for an ZTFobject in NO survey
    Then the request should return 400 error
