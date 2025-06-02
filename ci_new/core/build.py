import sys

import anyio
import dagger

from core.utils import PackageArgs, build, is_library, publish_lib


async def _build_package(packages: dict[str, PackageArgs], dry_run: bool):
    config = dagger.Config(log_output=sys.stdout)

    async with dagger.Connection(config) as client:
        async with anyio.create_task_group() as tg:
            for pkg, content in packages.items():
                build_args = list(zip(content["build-arg"], content["value"]))
                if is_library(pkg):
                    tg.start_soon(
                        publish_lib,
                        client,
                        content["package-dir"],
                        dry_run,
                    )
                else:
                    tg.start_soon(
                        build,
                        client,
                        content["package-dir"],
                        build_args,
                        pkg,
                        dry_run,
                    )


def build_packages(packages: dict[str, PackageArgs], dry_run: bool):
    anyio.run(_build_package, packages, dry_run)
