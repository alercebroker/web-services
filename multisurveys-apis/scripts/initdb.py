import argparse
import os

import yaml

from core.config.connection import psql_entity
from core.repository.queries.create_q3c_index import create_q3c_idx


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


def initdb():
    parser = argparse.ArgumentParser(description="Init database")
    parser.add_argument("service", type=str, help="the name of the service")
    args = parser.parse_args()
    config = (
        config_from_yaml().get("services").get(args.service).get("db_config")
    )

    # export db secrets
    os.environ["PSQL_USER"] = config["psql_user"]
    os.environ["PSQL_PASSWORD"] = config["psql_password"]
    os.environ["PSQL_DATABASE"] = config["psql_database"]
    os.environ["PSQL_HOST"] = config["psql_host"]
    os.environ["PSQL_PORT"] = str(config["psql_port"])
    os.environ["SCHEMA"] = config["psql_schema"]

    db = psql_entity()
    db.create_db()
    create_q3c_idx(db)


def create_q3c_idx_cmd():
    parser = argparse.ArgumentParser(description="Init database")
    parser.add_argument("service", type=str, help="the name of the service")
    args = parser.parse_args()
    config = (
        config_from_yaml().get("services").get(args.service).get("db_config")
    )

    # export db secrets
    os.environ["PSQL_USER"] = config["psql_user"]
    os.environ["PSQL_PASSWORD"] = config["psql_password"]
    os.environ["PSQL_DATABASE"] = config["psql_database"]
    os.environ["PSQL_HOST"] = config["psql_host"]
    os.environ["PSQL_PORT"] = str(config["psql_port"])
    os.environ["SCHEMA"] = config["psql_schema"]

    db = psql_entity()
    create_q3c_idx(db)
