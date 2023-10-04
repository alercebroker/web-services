import sys
import dagger
import os
import pathlib


def _get_publish_secret(client):
    gtoken = os.environ["GHCR_TOKEN"]
    secret = client.set_secret("gtoken", gtoken)
    return secret


async def _publish_container(
    container: dagger.Container,
    package_name: str,
    tags: list,
    secret: dagger.Secret,
):
    for tag in tags:
        addr = await container.with_registry_auth(
            f"ghcr.io/alercebroker/{package_name}:{tag}",
            "alerceadmin",
            secret,
        ).publish(f"ghcr.io/alercebroker/{package_name}:{tag}")
        print(f"published image at: {addr}")


async def git_push(dry_run: bool):
    config = dagger.Config(log_output=sys.stdout)

    async with dagger.Connection(config) as client:
        path = pathlib.Path().cwd().parent.absolute()
        container = (
            client.container()
            .from_("alpine:latest")
            .with_exec(["apk", "add", "--no-cache", "git"])
            .with_exec(
                ["git", "config", "--global", "user.name", '"@alerceadmin"']
            )
            .with_exec(
                [
                    "git",
                    "config",
                    "--global",
                    "user.email",
                    "alerceadmin@users.noreply.github.com",
                ]
            )
            .with_directory(
                "/web-services",
                client.host().directory(
                    str(path), exclude=[".venv/", "**/.venv/"]
                ),
            )
            .with_workdir("/web-services")
            .with_exec(["git", "status"])
        )
        if not dry_run:
            await (
                container.with_exec(["git", "add", "."])
                .with_exec(["git", "commit", "-m", "chore: update version"])
                .with_exec(["git", "push"])
            )
        else:
            await container


async def update_version(package_dir: str, version: str, dry_run: bool):
    config = dagger.Config(log_output=sys.stdout)

    async with dagger.Connection(config) as client:
        path = pathlib.Path().cwd().parent.absolute()
        # get build context directory
        source = (
            client.container()
            .from_("python:3.11-slim")
            .with_exec(["apt", "update"])
            .with_exec(["apt", "install", "git", "-y"])
            .with_exec(["pip", "install", "poetry"])
            .with_directory(
                "/web-services",
                client.host().directory(
                    str(path), exclude=[".venv/", "**/.venv/"]
                ),
            )
        )
        update_version_command = ["poetry", "version", version]
        if dry_run:
            update_version_command.append("--dry-run")

        await (
            source.with_workdir(f"/web-services/{package_dir}")
            .with_exec(update_version_command)
            .directory(".")
            .export(str(path / package_dir))
        )


async def build(package_dir: str, tags: list, dry_run: bool):
    config = dagger.Config(log_output=sys.stdout)

    async with dagger.Connection(config) as client:
        path = pathlib.Path().cwd().parent.absolute()
        # get build context directory
        context_dir = client.host().directory(
            str(path), exclude=[".venv/", "**/.venv/"]
        )
        # build using Dockerfile
        image_ref = await client.container().build(
            context=context_dir, dockerfile=f"{package_dir}/Dockerfile"
        )
        print(f"Built image with tag: {tags}")

        if not dry_run:
            print("Publishing image")
            # publish the resulting container to a registry
            secret = _get_publish_secret(client)
            await _publish_container(image_ref, package_dir, tags, secret)


async def get_tags(package_dir: str) -> list:
    config = dagger.Config(log_output=sys.stdout)

    async with dagger.Connection(config) as client:
        path = pathlib.Path().cwd().parent.absolute()
        # get build context directory
        source = (
            client.container()
            .from_("python:3.11-slim")
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


async def update_chart(chart_name: str, dry_run: bool):
    config = dagger.Config(log_output=sys.stdout)
    async with dagger.Connection(config) as client:
        path = pathlib.Path().cwd().parent.absolute()

        script = [
            "poetry",
            "run",
            "python",
            "build/chart_script.py",
            chart_name,
        ]
        if dry_run:
            script.append("--dry-run")
        await (
            client.container()
            .from_("python:3.11-slim")
            .with_exec(["pip", "install", "poetry"])
            .with_directory(
                "/web-services",
                client.host().directory(
                    str(path), exclude=[".venv/", "**/.venv/"]
                ),
            )
            .with_workdir("/web-services/ci")
            .with_exec(script)
            .directory("/web-services/charts")
            .export(str(path / "charts"))
        )
