import typer
import json
import anyio
from deploy.deploy_stage import deploy_stage

app = typer.Typer()

state_file_name = ".deploy_state.json"

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
):
    file = open(state_file_name, '+r')
    packages_dict = json.load(file)
    file.close()

    packages_dict[package] = {
        "packageName": package,
        "values": package if values is None else values,
        "chartFolder": package if chart_folder is None else chart_folder,
    }

    file = open(state_file_name, "w")
    json.dump(packages_dict, file)
    file.close()
    print(packages_dict)

@app.command()
def execute(
    stage: str,
    dry_run: bool = False
):
    file = open(state_file_name, 'r+')
    packages_dict = json.load(file)

    if stage not in ["staging", "production"]:
        raise ValueError(
            f'Invalid stage "{stage}". Valid stages are: staging, production'
        )
    anyio.run(deploy_stage, packages_dict, stage, dry_run)


if __name__ == "__main__":
    app()