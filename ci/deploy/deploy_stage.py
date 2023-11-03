import dagger
import os
import sys
import anyio
import pathlib
import logging

# Configure the logging settings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def env_variables(envs: dict[str, str]):
    def env_variables_inner(ctr: dagger.Container):
        for key, value in envs.items():
            ctr = ctr.with_env_variable(key, value)
        return ctr

    return env_variables_inner


def get_values(client: dagger.Client, path: str, ssm_parameter_name: str):
    def get_values_inner(ctr: dagger.Container):
        ctr = (
            ctr.with_directory(
                "/web-services",
                client.host().directory(path, exclude=[".venv/", "**/.venv/"]),
            )
            .with_workdir("/web-services/ci")
            .with_exec(["python", "-m", "pip", "install", "poetry"])
            .with_exec(["poetry", "install"])
            .with_exec(
                [
                    "poetry",
                    "run",
                    "python",
                    "./deploy/ssm.py",
                    ssm_parameter_name,
                ]
            )
        )
        return ctr

    return get_values_inner


async def helm_upgrade(package: str, stage: str, dry_run: bool):
    config = dagger.Config(log_output=sys.stdout)
    async with dagger.Connection(config) as client:
        k8s = (
            client.container()
            .from_("alpine/k8s:1.27.5")
            .with_(
                env_variables(
                    {
                        "AWS_ACCESS_KEY_ID": os.environ["AWS_ACCESS_KEY_ID"],
                        "AWS_SECRET_ACCESS_KEY": os.environ[
                            "AWS_SECRET_ACCESS_KEY"
                        ],
                        "AWS_SESSION_TOKEN": os.environ["AWS_SESSION_TOKEN"],
                        "AWS_DEFAULT_REGION": os.environ["AWS_DEFAULT_REGION"],
                        "STAGE": stage,
                    },
                )
            )
            .with_exec(
                [
                    "sh",
                    "-c",
                    """
                    aws eks update-kubeconfig \
                    --region us-east-1 \
                    --name ${STAGE} \
                    --alias ${STAGE}
                    """,
                ]
            )
        )
        helm_command = [
            "helm",
            "upgrade",
            "-i",
            "-f",
            "values.yaml",
            package,
            f"web-services/{package}",
        ]
        if dry_run:
            helm_command.append("--dry-run")

        await (
            k8s.with_exec(["kubectl", "config", "get-contexts"])
            .with_exec(
                [
                    "helm",
                    "repo",
                    "add",
                    "web-services",
                    "https://alercebroker.github.io/web-services",
                ]
            )
            .with_(
                get_values(
                    client,
                    str(pathlib.Path().cwd().parent.absolute()),
                    f"{package}-service-helm-values",
                )
            )
            .with_exec(helm_command)
        )


async def deploy_package(packages: list, stage: str, dry_run: bool):
    async with anyio.create_task_group() as tg:
        for package in packages:
            logger.info(f"Deploying {package} to stage {stage}")
            tg.start_soon(helm_upgrade, package, stage, dry_run)


async def deploy_stage(packages: list, stage: str, dry_run: bool):
    await deploy_package(packages, stage, dry_run)


if __name__ == "__main__":
    packages = ["lightcurve", "astroobject"]
    stage = "staging"
    anyio.run(deploy_stage, packages, stage, dry_run=True)
