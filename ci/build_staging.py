import anyio
from utils import build, get_tags, update_version, git_push


def _build_package(package_dir: str, do_publish: bool):
    tags = anyio.run(get_tags, package_dir)
    anyio.run(build, package_dir, tags, do_publish)


def _update_version(packages: list, do_push: bool):
    for package in packages:
        anyio.run(update_version, package, "prerelease")
    anyio.run(git_push, do_push)


def build_staging(do_publish: bool, do_push: bool):
    _update_version(["lightcurve", "astroobject"], do_push)
    _build_package("lightcurve", do_publish)
    _build_package("astroobject", do_publish)
