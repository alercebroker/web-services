import pathlib
import sys

import anyio
import dagger

from core.utils import git_push, is_library, update_version


async def _update_package_version(packages: list[str], version: str, dry_run: bool):
    config = dagger.Config(log_output=sys.stdout)
    path = pathlib.Path().cwd().parent.absolute()
    async with dagger.Connection(config) as client:
        source = (
            client.container()
            .from_("python:3.11-slim")
            .with_exec(["apt", "update"])
            .with_exec(["apt", "install", "git", "-y"])
            .with_exec(
                [
                    "git",
                    "config",
                    "--global",
                    "user.name",
                    '"@alerceadmin"',
                ]
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
            .with_exec(["pip", "install", "poetry"])
            .with_directory(
                "/build",
                client.host().directory(
                    str(path),
                    exclude=[
                        ".venv/",
                        "**/.venv/",
                        "*/.venv/",
                        "*.venv",
                        "tests/",
                        "**/tests/",
                    ],
                ),
            )
        )
        async with anyio.create_task_group() as tg:
            for package in packages:
                also_update_chart = not is_library(package)
                tg.start_soon(
                    update_version,
                    source,
                    path,
                    package,
                    version,
                    also_update_chart,
                    dry_run,
                )


def update_packages(packages, version, dry_run: bool):
    anyio.run(_update_package_version, packages, version, dry_run)
    anyio.run(git_push, dry_run)
