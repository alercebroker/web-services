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
    print(f"root folder {root_folder}\n\n\n")
    config_file_name = "config.yaml"
    config_file = os.path.join(root_folder, config_file_name)
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Config file {config_file} not found.")

    with open(config_file, "r") as file:
        config = yaml.safe_load(file)

    return config


def run():
    """
    Synchronous version of run_service.
    This is useful for running the service in a synchronous context.
    """
    config_dict = config_from_yaml()

    print(f"Config dict used:\n{config_dict}")
    buckets_config = config_dict["buckets_config"]

    for survey, values in buckets_config.items():

        os.environ[f"{survey}_BUCKET_REGION"] = values["bucket_region"]
        os.environ[f"{survey}_BUCKET_NAME"] = values["bucket_name"]

    uvicorn.run(
        f"src.{config_dict['source_folder']}.api:app",
        port=config_dict["port"],
        reload=config_dict.get("reload", True),
        reload_dirs=[".", "../libs"],
    )
