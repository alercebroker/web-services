## YAML Config file structure
The config that the apis will use to run will be defined in a yaml file in the root of the mulsituveys-apis folder.
This file will contian a list of services, one for each api the developer wish to run.

The strcuture of this file will be.

services:
    - object_api:
      source_folder: path
      url: url
      port: 8000
      env: staging
      db_config:
        psql_user: user
        psql_password: psw
        psql_database: db
        psql_host: host
        psql_port: port
        psql_schema: schema

    - lightcurve_apo:
      source_folder: path
      url: url
      port: 8000
      env: staging
      db_config:
        psql_user: user
        psql_password: psw
        psql_database: db
        psql_host: host
        psql_port: port
        psql_schema: schema


The run_all command will attempt to run all the apis that are included in the services list.


