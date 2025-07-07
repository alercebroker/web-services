import asyncio
import os
import sys
import yaml

import uvicorn

def config_from_yaml():
    """
    Read the config from a yaml file and return a dict.
    The file is expected to be in the root of the app.
    """
    import pathlib
    root_folder = pathlib.Path(__file__).parent.parent.resolve()
    config_file_name = "config.yaml" 
    config_file = os.path.join(root_folder, config_file_name)
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file {config_file} not found.")

    with open(config_file, "r") as file:
        config = yaml.safe_load(file)

    return config


###
### Define a single entry point for running the API services
### For each api service in the src folder.
###

def run_object():
    config_dict = config_from_yaml()    
    service_config = config_dict["services"]["object_api"]
    print(f"Running service: object_api with config: {service_config}")
    asyncio.run(run_service(service_config))


def run_lightcurve():
    config_dict = config_from_yaml()
    service_config = config_dict["services"]["lightcurve_api"]
    print(f"Running service: lightcurve_api with config: {service_config}")
    asyncio.run(run_service(service_config))

def run_magstat():
    config_dict = config_from_yaml()
    service_config = config_dict["services"]["magstat_api"]
    print(f"Running service: magstat_api with config: {service_config}")
    asyncio.run(run_service(service_config))

###
### A function to run all the services configured in the yaml file
###

def run():    
    asyncio.run(run_async())

async def run_async():
    """
    read the config from file

    for each service in the config
    run the service with the config dict
    """
    
    tasks = []
    config_dict = config_from_yaml()

    for service in config_dict["services"].keys():
        service_config = config_dict["services"][service]
        print(f"Creating task for service: {service} with config: {service_config}")
        tasks.append(asyncio.create_task(run_service(service_config)))

    first = asyncio.as_completed(tasks).__next__()
    await first
    for task in tasks:
        task.cancel("Shutting down")


async def run_service(
    config_dict: dict = None,
):  
    
    db_config = config_dict.get("db_config")

    server_config = uvicorn.Config(
        # put the db config
        f"{config_dict['source_folder']}.api:app",
        port=config_dict["port"],
        reload=config_dict.get("reload", True),
        reload_dirs=[".", "../libs"],
        root_path=config_dict["root_path"],
    )
    server = uvicorn.Server(server_config)
    os.environ["API_URL"] = config_dict["url"]
    # export db secrets
    os.environ["PSQL_USER"] = db_config["psql_user"]
    os.environ["PSQL_PASSWORD"] = db_config["psql_password"]
    os.environ["PSQL_DATABASE"] = db_config["psql_database"]
    os.environ["PSQL_HOST"] = db_config["psql_host"]
    os.environ["PSQL_PORT"] = str(db_config["psql_port"])
    os.environ["SCHEMA"] = db_config["psql_schema"]
    
    await server.serve()
