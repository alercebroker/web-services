import requests
from statistics import quantiles, mean, stdev


"""
The TARGET_URL should have curly braces tokens to placeholder for the
list of variations of urls to requests
"""
TARGET_URL = "{replacement}"

"""
A list of dictionarys is used to fill the TARGET_URL with data to create
the urls to be used in the requests.
"""
REQUEST_URL_SETUP = [
    {}
]

"""
Example of how would be used

TARGET_URL = localhost:8080?oid={oid}&survey_id=lsst

REQUEST_URL_SETUP = [
    {
        "oid": 1234
    },
    {
        "oid": 5678
    }
]
"""

REQUEST_URLS = [
    TARGET_URL.format(**d) for d in REQUEST_URL_SETUP
]


request_times = []

for u in REQUEST_URLS:
    response = requests.get(u)
    time = response.elapsed.total_seconds()
    request_times.append(time)


"""
Results:
    Average Time
    Std deviation
    Percentille 95
    Percentille 99
"""

results_percentilles = quantiles(request_times, n=100)
p99 = results_percentilles[99] #98?
p95 = results_percentilles[95] #94?
avg = mean(request_times)
std_dev = stdev(request_times)