import dagger
import anyio
import logging
from deploy.utils import (
    dagger_config,
    helm_package,
    helm_upgrade,
    helm_rollback,
    prepare_k8s_container,
)

# Configure the logging settings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def _deploy_package(packages: list, stage: str, dry_run: bool):
    async with anyio.create_task_group() as tg:
        for package in packages:
            async with dagger.Connection(dagger_config) as client:
                logger.info(f"Deploy {package} in {stage}")
                k8s = prepare_k8s_container(client, stage, stage, package)
                await tg.start(helm_package, k8s, package)
                await tg.start(helm_upgrade, k8s, package, dry_run)


async def _rollback_and_deploy_package(
    packages: list, stage: str, dry_run: bool
):
    from_repo = True
    async with anyio.create_task_group() as tg:
        for package in packages:
            async with dagger.Connection(dagger_config) as client:
                logger.info(f"Rollback and deploy {package} in {stage}")
                k8s = prepare_k8s_container(client, stage, stage, package)
                await tg.start(helm_rollback, k8s, package, dry_run)
                await tg.start(helm_upgrade, k8s, package, dry_run, from_repo)


async def deploy_stage(packages: list, stage: str, dry_run: bool):
    await _deploy_package(packages, stage, dry_run)


async def rollback_stage(packages: list, stage: str, dry_run: bool):
    await _rollback_and_deploy_package(packages, stage, dry_run)


if __name__ == "__main__":
    packages = ["lightcurve", "astroobject"]
    stage = "staging"
    anyio.run(deploy_stage, packages, stage, dry_run=True)
