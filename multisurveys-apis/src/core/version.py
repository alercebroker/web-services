from importlib.metadata import PackageNotFoundError, version

# pyproject.toml is the only place that holds the version; everything else reads it from the installed package.
# A stale local install reports a stale version: re-run `poetry install` after a bump.
try:
    APP_VERSION = version("multisurveys-apis")
except PackageNotFoundError:
    APP_VERSION = "dev"
