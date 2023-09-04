import sys
import dagger
import os
import pathlib


def get_publish_secret(client):
    gtoken = os.environ["GHCR_TOKEN"]
    secret = client.set_secret("gtoken", gtoken)
    return secret


def publish_container(
    container: dagger.Container,
    package_name: str,
    tags: list,
    secret: dagger.Secret,
):
    for tag in tags:
        addr = container.with_registry_auth(
            f"ghcr.io/alercebroker/{package_name}:{tag}",
            "alerceadmin",
            secret,
        )
        print(f"published image at: {addr}")


async def build(package_dir: str, tags: list, publish=False):
    config = dagger.Config(log_output=sys.stdout)

    async with dagger.Connection(config) as client:
        path = pathlib.Path().cwd().parent.absolute()
        # get build context directory
        context_dir = client.host().directory(
            str(path), exclude=[".venv/", "**/.venv/"]
        )
        # build using Dockerfile
        # publish the resulting container to a registry
        image_ref = await client.container().build(
            context=context_dir, dockerfile=f"{package_dir}/Dockerfile"
        )
        print(f"Built image with tag: {tags}")

        if publish:
            secret = get_publish_secret(client)
            publish_container(image_ref, package_dir, tags, secret)


async def get_tags(package_dir: str) -> list:
    config = dagger.Config(log_output=sys.stdout)

    async with dagger.Connection(config) as client:
        path = pathlib.Path().cwd().parent.absolute()
        # get build context directory
        source = (
            client.container()
            .from_("python:3.10-slim")
            .with_exec(["pip", "install", "poetry"])
            .with_directory(
                "/web-services",
                client.host().directory(
                    str(path), exclude=[".venv/", "**/.venv/"]
                ),
            )
        )

        runner = source.with_workdir(f"/web-services/{package_dir}").with_exec(
            ["poetry", "version", "--short"]
        )

        out = await runner.stdout()

    return ["rc", out.strip("\n")]
