import sys
import anyio
from build.build_stage import build_stage
from deploy.deploy_stage import deploy_stage, rollback_stage
from test.test_stage import test_stage


def build(packages: list, stage: str, dry_run=True) -> None:
    if stage == "staging":
        version = "prerelease"
    elif stage == "production":
        version = "release"
    else:
        raise ValueError(
            f'Invalid stage "{stage}". Valid stages are: staging, production'
        )
    anyio.run(build_stage, packages, version, dry_run)


def deploy(packages: list, stage: str = True, dry_run: bool = True) -> None:
    if stage not in ["staging", "production"]:
        raise ValueError(
            f'Invalid stage "{stage}". Valid stages are: staging, production'
        )
    anyio.run(deploy_stage, packages, stage, dry_run)


def test(packages: list, stage: str) -> None:
    if stage not in ["staging", "production"]:
        raise ValueError(
            f'Invalid stage "{stage}". Valid stages are: staging, production'
        )
    anyio.run(test_stage, packages, stage)


def rollback(packages: list, stage: str = True, dry_run: bool = True) -> None:
    if stage not in ["staging", "production"]:
        raise ValueError(
            f'Invalid stage "{stage}". Valid stages are: staging, production'
        )
    anyio.run(rollback_stage, packages, stage, dry_run)


if __name__ == "__main__":
    # poetry run python main.py deploy lightcurve,astroobject staging --dry-run
    command = sys.argv[1]
    packages = sys.argv[2].split(",")  # comma separated list of packages
    if len(packages) == 0:
        raise ValueError("No packages specified")
    stage = sys.argv[3]
    dry_run = False
    if len(sys.argv) > 4:
        dry_run = sys.argv[4]
        dry_run = dry_run == "--dry-run"
        print("Running with --dry-run")
    if command == "build":
        build(packages, stage, dry_run)
    if command == "deploy":
        deploy(packages, stage, dry_run)
    if command == "test":
        test(packages, stage)
    if command == "rollback":
        rollback(packages, stage)
