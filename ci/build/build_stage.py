import anyio
from common.utils import get_poetry_version
from build.utils import build, update_version, git_push, update_chart


async def _build_package(packages: list, dry_run: bool):
    async with anyio.create_task_group() as tg:
        for package in packages:
            tags = await get_poetry_version(package)
            tg.start_soon(build, package, tags, dry_run)


async def _update_package_version(packages: list, version: str, dry_run: bool):
    async with anyio.create_task_group() as tg:
        for package in packages:
            tg.start_soon(update_version, package, version, dry_run)


async def _update_chart_version(packages: list, dry_run: bool):
    async with anyio.create_task_group() as tg:
        for package in packages:
            tg.start_soon(update_chart, package, dry_run)


async def build_stage(packages: list, version: str, dry_run: bool):
    await _update_package_version(packages, version, dry_run)
    await _update_chart_version(packages, dry_run)
    await git_push(dry_run)
    await _build_package(packages, dry_run)

