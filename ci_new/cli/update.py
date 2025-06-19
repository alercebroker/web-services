from typer import Typer

from core.update import update_packages
from core.utils import Stage

app = Typer(
    help="""
    A group of commands to update the version of package of the Alerce Pipeline
    """
)


@app.command()
def version(
    packages: list[str],
    version: str,
    stage: Stage = Stage.staging,
    dry_run: bool = False,
):
    """
    Update the versions of a list of packages. Can be used with a single package.
    """
    match stage:
        case Stage.staging:
            update_packages(packages, "prerelease", dry_run)
        case Stage.production:
            update_packages(packages, version, dry_run)


if __name__ == "__main__":
    app()
