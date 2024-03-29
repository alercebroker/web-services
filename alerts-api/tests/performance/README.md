# Performance Tests

This test suite uses [k6](https://k6.io/docs/ "k6 Documentation")

To install the package you must add the source to the package manager:

### Ubuntu/Debian

```
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

### Fedora

```
sudo dnf install https://dl.k6.io/rpm/repo.rpm
sudo dnf install k6
```

If any further additions or modifications are to be added, please refer to the official documentation:

 - [Running k6](https://k6.io/docs/get-started/running-k6/ "Running k6")
 - [k6 Options](https://k6.io/docs/using-k6/k6-options/how-to "How to use options")
 - [k6 Javascript API](https://k6.io/docs/javascript-api/ "k6 JavaScript API")

## Test types

### Smoke test

There is no specific file for this type of test. It is integrated
in each of the other ones.

This test always runs at the beginning with a limited number of virtual users. 
Its goals are twofold:

* Check that the API is working correctly, independently of the load level.
* "Warm-up" the API for the scaling to take place on time.

### Load test

File: `load_tests.js`.

This tests the working of the API under standard load conditions. The number
of virtual users remain constant during the whole duration, and it checks the 
request time statistics under competing calls form the multiple users.

### Spike test

File: `spike_tests.js`.

Similar to the load tests, but with the number of virtual users changing during
the execution. This mainly translates to spikes with a large number of users, 
but short duration happening in the middle of a standard load. This checks indirectly
the effectiveness of the API scaling and the refractory period needed to come back 
to a standard level.

Note that the spikes in each scenario do not occur simultaneously, but this can
be modified in the respective file.

### Stress test

File: `stress_tests.js`.

Checks the breaking point of the API. The number of virtual users is constantly
increasing (up to a maximum of 300). This is the only test that can exit before completion
at any point in which 10% of the requests fails (configurable in file). Under normal 
conditions, most of these failures should be due to timeouts as the request queue grows 
beyond the reply capacity. The number of virtual users at this point is considered 
the maximum capacity for the API.

## Workflows

### Full frontend workflow

**Runs for all tests.**

This represents the standard workflow when using the explorer frontend. This 
scenario is only used within the smoke and stress tests.

* The user queries the `objects` endpoint based on a series of parameters
* The user browses the list (represented by sleep time)
* The user selects an object, requests its info and views it (represented by sleep time)

### Mock frontend workflow

**Runs for load tests and spike tests.**

This is represented by six individual scenarios and represents the usage of the explorer, 
but now split by type of requests. 

* Starts with queries for objects classified as stochastic, transients and variables (one per scenario).
  * These will run alone at the beginning of the test.
* Retrieve info about a single object (magstats, probabilities and the lightcurve). 
  * There are 3 scenarios for light, medium and heavy objects.
    * **Light objects**: 0 to 10 detections
    * **Medium objects**: 10 to 100 detections
    * **Heavy objects**: more than 100 detections
  * These scenarios overlap with the queries, but keep on running for a while after they finished.

Note that sleep times after each request (or bulk request in the case of individual objects) are still present as in previous workflow.

### Accessing detections for a list

**Runs for load tests and spike tests.**

This emulates automated searches, assuming the user if familiar with the OIDs of interest.

* Given a list of objects, request only the detections in rapid succession.
* The detections for each object are retrieved, without a pause in between object requests.
* As with above workflow, the lists consist of either light, medium or heavy objects.
* Each of the three types are run concurrently.
