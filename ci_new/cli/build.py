import json

from typer import Option, Typer

from core.build import build_packages
from core.utils import PackageArgs

app = Typer(
    help="""
    Group of commands to build packages of the Alerce pipeline.

    There are two ways to build packages.
    
    1- A single build accion calling the direct command.
        eg: python main.py build direct package_name

    2- A bulk build acction, this involved 3 commands: prepare,
       add_package and execute.
        eg: 
        poetry run python main.py build prepare
        poetry run python main.py build add-package package_name_1
        poetry run python main.py build add-package package_name_2
        poetry run python main.py build execute
    """
)

state_file_name = ".build_state.json"


def _build_package_dict(package_dir: str | None, arg_strs: list[str]) -> PackageArgs:
    if len(arg_strs) == 0:
        return {"build-arg": [], "value": [], "package-dir": package_dir}

    split_args = list(map(lambda arg: arg.split(":"), arg_strs))
    args, values = list(zip(*split_args))

    return {"build-arg": args, "value": values, "package-dir": package_dir}


@app.command()
def prepare():
    """
    Start the bulk build proccess by seting up the environment.
    """
    empty_dict = {}
    file = open(state_file_name, "w")
    json.dump(empty_dict, file)
    file.close()


@app.command()
def execute(dry_run: bool = False, clear: bool = False):
    """
    Executes the bulk build process according to the environment previously setted up.
    """
    file = open(state_file_name, "r+")
    packages_dict = json.load(file)
    build_packages(packages_dict, dry_run)
    if clear:
        file.truncate(0)
    file.close()


@app.command()
def direct(
    package: str,
    package_dir: str = None,
    build_args: list[str] = [],
    dry_run: bool = False,
):
    """
    Builds a single package.
    """
    if package_dir is None:
        package_dir = package
    package_dict = _build_package_dict(package_dir, build_args)
    build_packages({package: package_dict}, dry_run)


@app.command()
def add_package(
    package: str, package_dir: str = None, build_args: list[str] = Option()
):
    """
    Update the environment setup to add a package to be deployed in bulk
    with other packages.
    """
    if package_dir is None:
        package_dir = package

    file = open(state_file_name, "+r")
    packages_dict = json.load(file)
    file.close()

    package_dict = _build_package_dict(package_dir, build_args)

    packages_dict[package] = package_dict

    file = open(state_file_name, "w")
    json.dump(packages_dict, file)
    file.close()


if __name__ == "__main__":
    app()
