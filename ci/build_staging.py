import anyio
from utils import build, get_tags


def build_staging():
    tags = anyio.run(get_tags, "lightcurve")
    anyio.run(build, "lightcurve", tags)
