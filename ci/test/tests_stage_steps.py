import dagger
import sys
from test.tests import healthcheck_test


async def healthcheck_test_step(url: str):
    config = dagger.Config(log_output=sys.stdout)
    async with dagger.Connection(config) as client:
        container = (
            client.container()
            .from_("python:3.11-slim")
            .with_exec(["pip", "install", "httpx"])
        )
        # Execute the healthcheck test inside the container
        container.run(healthcheck_test, url)
