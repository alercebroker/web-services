import typer
import json
import anyio
from deploy.deploy_stage import rollback_stage

app = typer.Typer()

state_file_name = ".rollback_state.json"

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
        "values": values if values is None else values,
        "chartFolder": chart_folder if chart_folder is None else chart_folder,
    }

    file = open(state_file_name, "w")
    json.dump(packages_dict, file)
    file.close()

@app.command()
def execute(
    stage: str,
    dry_run: bool = False
):
    file = open(state_file_name, 'r+')
    packages_dict = json.load(file)
    
    try:
        anyio.run(rollback_stage, packages_dict, stage, dry_run)
    except Exception as e:
        print(f"Error response: {e}")
    
if __name__ == "__main__":
    app()