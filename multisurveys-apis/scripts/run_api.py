import asyncio
import os
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
    # Use the sync version of run_service to run the FastAPI app
    run_service(service_config)


def run_lightcurve():
    config_dict = config_from_yaml()
    service_config = config_dict["services"]["lightcurve_api"]
    print(f"Running service: lightcurve_api with config: {service_config}")
    run_service(service_config)


def run_magstat():
    config_dict = config_from_yaml()
    service_config = config_dict["services"]["magstat_api"]
    print(f"Running service: magstat_api with config: {service_config}")
    run_service(service_config)


def run_classifier():
    config_dict = config_from_yaml()
    service_config = config_dict["services"]["classifier_api"]
    print(f"Running service: classifier_api with config: {service_config}")
    run_service(service_config)


def run_probability():
    config_dict = config_from_yaml()
    service_config = config_dict["services"]["probability_api"]
    print(f"Running service: probability_api with config: {service_config}")
    run_service(service_config)


def run_crossmatch():
    config_dict = config_from_yaml()
    service_config = config_dict["services"]["crossmatch_api"]
    print(f"Running service: crossmatch_api with config: {service_config}")
    run_service(service_config)

def run_stamp():
    config_dict = config_from_yaml()
    service_config = config_dict["services"]["stamp_api"]
    os.environ["LSST_BUCKET_REGION"] = service_config.get("lsst_bucket_region", "")
    os.environ["LSST_BUCKET_NAME"] = service_config.get("lsst_bucket_name", "")
    os.environ["ZTF_BUCKET_REGION"] = service_config.get("ztf_bucket_region", "")
    os.environ["ZTF_BUCKET_NAME"] = service_config.get("ztf_bucket_name", "")
    print(f"Running service: stamp_api with config: {service_config}")
    run_service(service_config)


def run_aladin():
    config_dict = config_from_yaml()
    service_config = config_dict["services"]["aladin_api"]
    print(f"Running service: aladin_api with config: {service_config}")
    run_service(service_config)


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
        print(f"Creating task for service: {service}")
        tasks.append(asyncio.create_task(async_run_service(service_config)))

    first = asyncio.as_completed(tasks).__next__()
    await first
    for task in tasks:
        task.cancel("Shutting down")


async def async_run_service(
    config_dict: dict = {},
):
    db_config = config_dict.get("db_config", {})

    server_config = uvicorn.Config(
        # put the db config
        f"{config_dict['source_folder']}.api:app",
        port=config_dict["port"],
        reload=config_dict.get("reload", True),
        reload_dirs=[".", "../libs"],
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


def run_service(
    config_dict: dict = {},
):
    """
    Synchronous version of run_service.
    This is useful for running the service in a synchronous context.
    """
    db_config = config_dict.get("db_config", {})

    os.environ["API_URL"] = config_dict["url"]
    # export db secrets
    os.environ["PSQL_USER"] = db_config["psql_user"]
    os.environ["PSQL_PASSWORD"] = db_config["psql_password"]
    os.environ["PSQL_DATABASE"] = db_config["psql_database"]
    os.environ["PSQL_HOST"] = db_config["psql_host"]
    os.environ["PSQL_PORT"] = str(db_config["psql_port"])
    os.environ["SCHEMA"] = db_config["psql_schema"]
    os.environ["USE_ABSOLUTE"] = config_dict.get("use_absolute", "false")

    uvicorn.run(
        f"src.{config_dict['source_folder']}.api:app",
        port=config_dict["port"],
        reload=config_dict.get("reload", True),
        reload_dirs=[".", "../libs"],
    )
