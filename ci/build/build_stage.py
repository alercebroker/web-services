import anyio
from common.utils import get_poetry_version
from build.utils import build, update_version, git_push, update_chart


async def _build_package(packages: dict, dry_run: bool):
    async with anyio.create_task_group() as tg:
        """
        for package in packages:
            tags = await get_poetry_version(package)
            tg.start_soon(build, package, tags, dry_run)
        """
        tags = await get_poetry_version(packages)
        try:
            tg.start_soon(build, packages, tags, dry_run)
        except Exception as e:
            print(f"Error response: {e}")

async def _update_package_version(packages: dict, version: str, dry_run: bool):
    async with anyio.create_task_group() as tg:
        """
        for package in packages:
            tg.start_soon(update_version, package, version, dry_run)
        """
        try:
            tg.start_soon(update_version, packages, version, dry_run)
        except Exception as e:
            print(f"Error response: {e}")

async def _update_chart_version(packages: dict, dry_run: bool):
    async with anyio.create_task_group() as tg:
        """
        for package in packages:
            tg.start_soon(update_chart, package, dry_run)
        """
        try:
            tg.start_soon(update_chart, packages, dry_run)
        except Exception as e:
            print(f"Error response: {e}")

async def build_stage(packages: dict, version: str, dry_run: bool):
    try:
        await _update_package_version(packages, version, dry_run)
        await _update_chart_version(packages, dry_run)
        await git_push(dry_run)
        await _build_package(packages, dry_run)
    except Exception as e:
        print(f"Error response: {e}")

