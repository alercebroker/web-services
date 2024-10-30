import typer
import json
import anyio
import pprint
from build.build_stage import build_stage

app = typer.Typer()

state_file_name = ".build_state.json"

@app.command()
def prepare():
    empty_dict = {}
    file = open(state_file_name, "w")
    json.dump(empty_dict, file)
    file.close()

@app.command()
def add_package(
    package: str,
    package_folder: str,
    chart_folder: str = None,
    chart_name: str = None,
):
    file = open(state_file_name, '+r')
    packages_dict = json.load(file)
    file.close()

    packages_dict[package] = {
        "packageName": package,
        "packageFolder": package_folder,
        "chartName": chart_name if chart_name is None else chart_name,
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
    print(packages_dict)
    if stage == "staging":
        version = "prerelease"
    elif stage == "production":
        version = "release"
    else:
        raise ValueError(
            f'Invalid stage "{stage}". Valid stages are: staging, production'
        )
    
    
    try:
        anyio.run(build_stage, packages_dict, version, dry_run)
    except Exception as e:
        print(f"Error response: {e}")
    
if __name__ == "__main__":
    app()