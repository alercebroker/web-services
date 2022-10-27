# Performance Tests

Tests run in k6

## Test types

### Smoke test

### Load test

### Stress test

## Workflows

### Full frontend workflow

This represents the standard workflow when using the explorer frontend. This 
scenario is only used within the smoke test as a warm-up to get the scaling of the API
ready for the rest of the tests.

* The user queries the `objects` endpoint based on a series of parameters
* The user browses the list (represented by sleep time)
* The user selects an object, requests its info and views it (represented by sleep time)

### Mock frontend workflow

This is represented by six individual scenarios and represents the usage of the explorer, 
but now split by type of requests. 

* Starts with queries for objects classified as stochastic, transients and variables (one per scenario).
  * These will run alone at the beginning of the test.
* Retrieve info about a single object (magstats, probabilities and the lightcurve). 
  * There are 3 scenarios for light, medium and heavy objects.
  * *(explain what the limits on for each are)*
  * These scenarios overlap with the queries, but keep on running for a while after they finished.

Note that sleep times after each request (or bulk request in the case of individual objects) are still present as in previous workflow

### Accessing detections for a list

This emulates automated searches, assuming the user if familiar with the OIDs of interest.

* Given a list of objects, request only the detections in rapid succession.
* The detections for each object are retrieved, without a pause in between object requests.
* As with above workflow, the lists consist of either light, medium or heavy objects.
* Each of the three types are run concurrently.
