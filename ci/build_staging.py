import anyio
from utils import build, get_tags, update_version, git_push


def _build_package(package_dir: str, do_publish: bool, do_push: bool):
    anyio.run(update_version, package_dir, "prerelease")
    anyio.run(git_push, do_push)
    tags = anyio.run(get_tags, package_dir)
    anyio.run(build, package_dir, tags, do_publish)


def build_staging(do_publish: bool, do_push: bool):
    _build_package("lightcurve", do_publish, do_push)
    _build_package("astroobject", do_publish, do_push)
