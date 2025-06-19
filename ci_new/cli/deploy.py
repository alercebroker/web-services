import json

from typer import Typer

from core.deploy import deploy
from core.utils import ChartArgs, Stage

app = Typer(
    help="""
    Group of commands to deploy packages of the Alerce pipeline.

    There are two ways to deploy packages.
    
    1- A single deploy accion calling the direct command.
        eg: python main.py deploy direct package_name

    2- A bulk deploy acction, this involved 3 commands: prepare,
       add_package and execute.
        eg: 
        poetry run python main.py deploy prepare
        poetry run python main.py deploy add-package package_name_1
        poetry run python main.py deploy add-package package_name_2
        poetry run python main.py deploy execute
    """
)

state_file_name = ".deploy_state.json"


def _build_chart_args(chart: str, values: str, chart_folder: str) -> ChartArgs:
    return {"chart": chart, "values": values, "chart-folder": chart_folder}


@app.command()
def prepare():
    """
    Start the bulk deploy proccess by seting up the environment.
    """
    empty_dict = {}
    file = open(state_file_name, "w")
    json.dump(empty_dict, file)
    file.close()


@app.command()
def execute(stage: Stage = Stage.staging, dry_run: bool = False, clear: bool = False):
    """
    Executes the bulk deploy process according to the environment previously setted up.
    """
    file = open(state_file_name, "r+")
    packages_dict = json.load(file)
    _deploy(packages_dict, stage, dry_run)
    if clear:
        file.truncate(0)
    file.close()


@app.command()
def direct(
    package: str,
    chart_folder: str = None,
    values: str = None,
    chart: str = None,
    stage: Stage = Stage.staging,
    dry_run: bool = False,
):
    """
    Deploy a single package.
    """
    if chart_folder is None:
        chart_folder = package
    if values is None:
        values = package
    if chart is None:
        chart = package

    package_dict = {}
    package_dict[package] = _build_chart_args(chart, values, chart_folder)

    _deploy(package_dict, stage, dry_run)


@app.command()
def add_package(
    package: str,
    chart_folder: str = None,
    values: str = None,
    chart: str = None,
):
    """
    Update the environment setup to add a package to be deployed in bulk
    with other packages.
    """
    if chart_folder is None:
        chart_folder = package
    if values is None:
        values = package
    if chart is None:
        chart = package

    file = open(state_file_name, "+r")
    packages_dict = json.load(file)
    file.close()

    packages_dict[package] = _build_chart_args(chart, values, chart_folder)

    file = open(state_file_name, "w")
    json.dump(packages_dict, file)
    file.close()


def _deploy(packages: dict[str, ChartArgs], stage: Stage, dry_run: bool):
    """
    Call the deploy staging or deploy producction according to stage
    with the packages dict. Essentially a wrapper.
    """
    match stage:
        case Stage.staging:
            deploy(packages, dry_run)
        case Stage.production:
            deploy(packages, dry_run)


if __name__ == "__main__":
    app()
