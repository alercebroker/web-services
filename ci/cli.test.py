import typer
import json
import anyio

from test.test_stage import test_stage


app = typer.Typer()

@app.command()
def execute(
    stage: str,
):
    file = open(state_file_name, 'r+')
    packages_dict = json.load(file)

    if stage not in ["staging", "production"]:
        raise ValueError(
            f'Invalid stage "{stage}". Valid stages are: staging, production'
        )
    anyio.run(test_stage, packages_dict, stage)

if __name__ == "__main__":
    app()
