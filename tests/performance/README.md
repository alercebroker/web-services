# Performance Tests

Tests run in k6

## Frontend Scenario

 - The user queries the objects endpoint, which contains some parameters
 - The user "sleeps" (this should mean the user is browsing)
 - The user selects an object and queries their info (lightcurve, probabilities and magstats)

## Parameters

 - **OBJECT_TYPE**: An object type is classified depending on the number of detections it has.
  - Light: 0 to 10 detections
  - Medium: 10 to 100 detections
  - Heavy: More than 100 detections