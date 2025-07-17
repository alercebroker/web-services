## YAML Config file structure
The config that the apis will use to run will be defined in a yaml file in the root of the mulsituveys-apis folder.
This file will contian a list of services, one for each api the developer wish to run.

The strcuture of this file will be.

services:
  object_api:
    source_folder: object_api
    root_path: /
    url: http://localhost:8000
    port: 8000
    env: dev
    db_config:
      psql_user: userr
      psql_password: psqw
      psql_database: db
      psql_host: host
      psql_port: 5432
      psql_schema: schema
  lightcurve_api:
    source_folder: lightcurve_api
    root_path: /
    url: http://localhost:8001
    port: 8001
    env: staging
    db_config:
      psql_user: userr
      psql_password: psqw
      psql_database: db
      psql_host: host
      psql_port: 5432
      psql_schema: schema


The run_all command will attempt to run all the apis that are included in the services list.


