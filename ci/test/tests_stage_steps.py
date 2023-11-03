import pathlib
import sys
import dagger


async def healthcheck_test_step(url: str):
    config = dagger.Config(log_output=sys.stdout)
    async with dagger.Connection(config) as client:
        path = str(pathlib.Path().cwd().parent.absolute())
        container = (
            client.container()\
            .from_("python:3.11-slim")
            .with_directory(
                "/web-services",
                client.host().directory(path, exclude=[".venv/", "**/.venv/"]),
            )
            .with_workdir("/web-services/ci/test")
            .with_exec(["pip", "install", "httpx"])
            # Execute the healthcheck test inside the container
            .with_exec(["python", "tests.py", "healthcheck", f"{url}"])
        )
