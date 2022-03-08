![](https://github.com/alercebroker/ztf-api-new/workflows/Tests/badge.svg) 
[![codecov](https://codecov.io/gh/alercebroker/ztf-api-new/branch/master/graph/badge.svg)](https://codecov.io/gh/alercebroker/ztf-api-new) 
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pyVersion38](https://img.shields.io/badge/python-3.8-blue.svg)](https://www.python.org/download/releases/3.8/)

# ALeRCE Alerts API

## Official documentation 

- [ALeRCE ZTF API Documentation](https://api.alerce.online/ztf/v1/)

## For developers

Clone this repo using `git clone https://github.com/alercebroker/ztf-api.git` and install requirements with `pip install -r requirements.txt`.

For modify an existing endpoint, go to `api/sql` and enter the folder of the endpoint that you want to modify. Only write code to specific task of this endpoint.

If you want to create a new endpoint, create a package with your new routines in `api/sql`. After that in the `api/app.py`, import the new logic in the top and add the namespace to the main api object. 

To run in develop, first you must set the following environment variables:

```
DB_HOST=
DB_PASSWORD=
DB_USER=
DB_DATABASE=
```

**Note:** If you don't have a database, you can create it using [db-plugins](https://github.com/alercebroker/db-plugins) and [Docker](https://github.com/alercebroker/pipeline-integration-test/blob/main/initdb/Dockerfile).

After run 

```
python scripts/run_server.py
```

## Production

### Build container

```
docker build -t ztf-api:<version> .
```

### Run container

```
docker run -e DB_DATABASE=<DB_DATABASE> -e DB_HOST=<DB_HOST> -e DB_PASSWORD=<DB_PASSWORD> -e DB_USER=<DB_USER> -d --name ztf-api-<suffix> -p 8082:8082 ztf-api:<version>
```
