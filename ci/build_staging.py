import anyio
from utils import build, get_tags, update_version


def build_staging(publish: bool):
    anyio.run(update_version, "lightcurve", "prerelease")
    tags = anyio.run(get_tags, "lightcurve")
    anyio.run(build, "lightcurve", tags, publish)
