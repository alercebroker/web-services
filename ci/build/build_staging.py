import anyio
from build.utils import build, get_tags, update_version, git_push, update_chart
from multiprocessing import Process


def _build_package(package_dir: str, dry_run: bool):
    tags = anyio.run(get_tags, package_dir)
    anyio.run(build, package_dir, tags, dry_run)


def _update_package_version(packages: list, dry_run: bool):
    for package in packages:
        anyio.run(update_version, package, "prerelease", dry_run)


def _update_chart_version(packages: list, dry_run: bool):
    for package in packages:
        anyio.run(update_chart, package, dry_run)


def build_staging(dry_run: bool):
    packages = ["lightcurve", "astroobject"]
    _update_package_version(packages, dry_run)
    _update_chart_version(packages, dry_run)
    anyio.run(git_push, dry_run)
    for package in packages:
        p = Process(target=_build_package, args=[package, dry_run])
        p.start()
