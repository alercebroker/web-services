import anyio
from utils import build, get_tags, update_version, git_push, update_chart
from multiprocessing import Process


def _build_package(package_dir: str, dry_run: bool):
    tags = anyio.run(get_tags, package_dir)
    anyio.run(build, package_dir, tags, dry_run)


def _update_version(packages: list, dry_run: bool):
    for package in packages:
        anyio.run(update_version, package, "prerelease", dry_run)
    anyio.run(git_push, dry_run)


def _update_chart(package: str, dry_run: bool):
    anyio.run(update_chart, package, dry_run)


def update_chart_staging(dry_run: bool):
    packages = ["lightcurve", "astroobject"]

    for package in packages:
        p = Process(target=_update_chart, args=[package, dry_run])
        p.start()


def build_staging(dry_run: bool):
    packages = ["lightcurve", "astroobject"]
    _update_version(packages, dry_run)
    for package in packages:
        p = Process(target=_build_package, args=[package, dry_run])
        p.start()
