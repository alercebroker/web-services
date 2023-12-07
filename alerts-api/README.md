![](https://github.com/alercebroker/ztf_api-new/workflows/Tests/badge.svg) 
[![codecov](https://codecov.io/gh/alercebroker/ztf_api/branch/master/graph/badge.svg?token=UHM0AV87S5)](https://codecov.io/gh/alercebroker/ztf_api)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pyVersion38](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/download/releases/3.8/)

# ALeRCE Alerts API

## Official documentation 

- [ALeRCE ZTF API Documentation](https://api.alerce.online/ztf/v1/)

## For developers

Clone this repo using `git clone https://github.com/alercebroker/ztf_api.git` and install requirements with `pip install -r requirements.txt`.

For modify an existing endpoint, go to `api/resources` and enter the folder of the endpoint that you want to modify. Only write code to specific task of this endpoint.

If you want to create a new endpoint, create a package with your new routines in `api/resources`. After that in the `api/app.py`, import the new logic in the top and add the namespace to the main api object. 

To run in develop, first you must set the following environment variables:

```
#Configure API port
PORT = 5000

# Config to connect to the PSQL Database
PSQL_HOST = 
PSQL_DATABASE = 
PSQL_USER = 
PSQL_PASSWORD = 
PSQL_PORT = 

# Config to connect to the MongoDB Database
MONGO_HOST = 
MONGO_PORT = 
MONGO_DATABASE = 
MONGO_AUTH_SOURCE = 
MONGO_USER = 
MONGO_PASSWORD = 

# optional config to indicate if the app should connect to a especific database.
CONNECT_PSQL = "default yes" 
CONNECT_MONGO = "default not set"
```

**Note:** If you don't have a database, you can create it using [db-plugins](https://github.com/alercebroker/db-plugins) and [Docker](https://github.com/alercebroker/pipeline-integration-test/blob/main/initdb/Dockerfile).

After run 

```
python scripts/run_server.py
```

## Using Docker

### Build container

```
docker build -t alerts-api:<version> .
```

### Run container

```
docker run -e [list of env variables] -d --name alerts-api -p 5000:5000 alerts-api:<version>
```

### Run image from the registry

1. RC image (staging)
```
docker run -e [list of env variables] -d --name alerts-api -p 5000:5000 ghcr.io/alercebroker/alerts_api:rc-<hash>
```

2. Latest image (production)
```
docker run -e [list of env variables] -d --name alerts-api -p 5000:5000 ghcr.io/alercebroker/alerts_api:latest
```
