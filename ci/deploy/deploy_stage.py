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


async def _deploy_package_task(client, package: str, stage: str, dry_run: bool):
    logger.info(f"Deploy {package} in {stage}")
    k8s = prepare_k8s_container(client, stage, stage, package)
    k8s = helm_package(k8s, package)
    k8s = helm_upgrade(k8s, package, dry_run)
    await k8s


async def _rollback_package_task(client, package: str, stage: str, dry_run: bool):
    logger.info(f"Deploy {package} in {stage}")
    k8s = prepare_k8s_container(client, stage, stage, package)
    k8s = helm_rollback(k8s, package, dry_run)
    k8s = helm_upgrade(k8s, package, dry_run, from_repo=True)
    await k8s


async def deploy_stage(packages: list, stage: str, dry_run: bool):
    async with dagger.Connection(dagger_config) as client:
        async with anyio.create_task_group() as tg:
            for package in packages:
                tg.start_soon(_deploy_package_task, client, package, stage, dry_run)


async def rollback_stage(packages: list, stage: str, dry_run: bool):
    async with dagger.Connection(dagger_config) as client:
        async with anyio.create_task_group() as tg:
            for package in packages:
                tg.start_soon(_rollback_package_task, client, package, stage, dry_run)  

if __name__ == "__main__":
    packages = ["lightcurve", "astroobject"]
    stage = "staging"
    anyio.run(deploy_stage, packages, stage, dry_run=True)
