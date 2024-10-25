import sys
import anyio
import typer
import json
from build.build_stage import build_stage
from deploy.deploy_stage import deploy_stage, rollback_stage
from test.test_stage import test_stage

app = typer.Typer()

state_file_name = ".deploy_state.json"


def build(packages: list, stage: str, dry_run=True) -> None:
    if stage == "staging":
        version = "prerelease"
    elif stage == "production":
        version = "release"
    else:
        raise ValueError(
            f'Invalid stage "{stage}". Valid stages are: staging, production'
        )
    anyio.run(build_stage, packages, version, dry_run)


def deploy(packages: dict, stage: str = True, dry_run: bool = True) -> None:
    if stage not in ["staging", "production"]:
        raise ValueError(
            f'Invalid stage "{stage}". Valid stages are: staging, production'
        )
    anyio.run(deploy_stage, packages, stage, dry_run)


def test(packages: list, stage: str) -> None:
    if stage not in ["staging", "production"]:
        raise ValueError(
            f'Invalid stage "{stage}". Valid stages are: staging, production'
        )
    anyio.run(test_stage, packages, stage)


def rollback(packages: list, stage: str = True, dry_run: bool = True) -> None:
    if stage not in ["staging", "production"]:
        raise ValueError(
            f'Invalid stage "{stage}". Valid stages are: staging, production'
        )
    anyio.run(rollback_stage, packages, stage, dry_run)  

@app.command()
def prepare():
    empty_dict = {}
    file = open(state_file_name, "w")
    json.dump(empty_dict, file)
    file.close()

@app.command()
def add_package(
    package: str,
    chart_folder: str = None,
    values: str = None,
    chart: str = None,
):
    file = open(state_file_name, '+r')
    packages_dict = json.load(file)
    file.close()

    packages_dict[package] = {
        "chart": package if chart is None else chart,
        "values": package if values is None else values,
        "chart-folder": package if chart_folder is None else chart_folder,
    }

    file = open(state_file_name, "w")
    json.dump(packages_dict, file)
    file.close()
    print(packages_dict)

@app.command()
def execute(
    action: str,
    stage: str,
    dry_run: bool = False
):
    file = open(state_file_name, 'r+')
    packages_dict = json.load(file)

    if action == "build":
        print(f"actions es: {action} {stage}")
        #build(lightcurve, probability, xmatch, magstats, object_details, stage, dry_run)
    if action == "deploy":
        print(f"actions es: {action} {stage}")
        deploy(packages_dict, stage, dry_run)
    if action == "test":
        print(f"actions es: {action} {stage}")
        #test(lightcurve, probability, xmatch, magstats, object_details, stage, dry_run)
    if action == "rollback":
        print(f"actions es: {action} {stage}")
        #rollback(lightcurve, probability, xmatch, magstats, object_details, stage, dry_run)

if __name__ == "__main__":
    app()



"""
if __name__ == "__main__":
    # poetry run python main.py deploy lightcurve,astroobject staging --dry-run

    # poetry run python main.py deploy lightcurve, test1, test2 staging --dry-run
    command = sys.argv[1]
    packages = sys.argv[2].split(",")  # comma separated list of packages
    print(sys.argv)
    if len(packages) == 0:
        raise ValueError("No packages specified")
    stage = sys.argv[3]
    dry_run = False
    if len(sys.argv) > 4:
        dry_run = sys.argv[4]
        dry_run = dry_run == "--dry-run"
        print("Running with --dry-run")
    if command == "build":
        build(packages, stage, dry_run)
    if command == "deploy":
        print("hola")
        deploy(packages, stage, dry_run)
    if command == "test":
        test(packages, stage)
    if command == "rollback":
        rollback(packages, stage)
"""