import os
import pathlib
import sys
from anyio import TASK_STATUS_IGNORED
from anyio.abc import TaskStatus
import dagger
from common.utils import set_environment, current_chart_version

dagger_config = dagger.Config(log_output=sys.stdout)


def get_configure_aws_command(cluster_name, cluster_alias):
    return [
        "sh",
        "-c",
        f"""
        aws eks update-kubeconfig \
        --region us-east-1 \
        --name {cluster_name} \
        --alias {cluster_alias}
        """,
    ]


def prepare_k8s_container(
    client: dagger.Client, cluster_name: str, cluster_alias: str, package: str
) -> dagger.Container:
    k8s_container = (
        client.container()
        .from_("alpine/k8s:1.27.5")
        .with_(
            set_environment(
                {
                    "AWS_ACCESS_KEY_ID": os.environ["AWS_ACCESS_KEY_ID"],
                    "AWS_SECRET_ACCESS_KEY": os.environ[
                        "AWS_SECRET_ACCESS_KEY"
                    ],
                    "AWS_SESSION_TOKEN": os.environ["AWS_SESSION_TOKEN"],
                    "AWS_DEFAULT_REGION": os.environ["AWS_DEFAULT_REGION"],
                },
            )
        )
        .with_exec(get_configure_aws_command(cluster_name, cluster_alias))
        .with_exec(["kubectl", "config", "get-contexts"])
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
    )
    return k8s_container


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


async def helm_package(
    k8s: dagger.Container,
    package: str,
    *,
    task_status: TaskStatus[None] = TASK_STATUS_IGNORED,
):
    helm_package_command = [
        "helm",
        "package",
        f"/web-services/charts/{package}/",
    ]

    await k8s.with_exec(helm_package_command)
    task_status.started()  # Release task lock


async def helm_upgrade(
    k8s: dagger.Container,
    package: str,
    dry_run: bool,
    from_repo: bool = False,
    *,
    task_status: TaskStatus[None] = TASK_STATUS_IGNORED,
):
    version = await current_chart_version(package)
    helm_upgrade_command = [
        "helm",
        "upgrade",
        "-i",
        "-f",
        "values.yaml",
        package,
    ]
    if from_repo:
        helm_upgrade_command.append(f"web-services/{package}")
    else:
        helm_upgrade_command.append(f"./{package}-{version}.tgz")
    if dry_run:
        helm_upgrade_command.append("--dry-run")

    await k8s.with_exec(helm_upgrade_command)
    task_status.started()  # Release task lock


async def helm_rollback(
    k8s: dagger.Container,
    package: str,
    dry_run: bool,
    task_status: TaskStatus[None] = TASK_STATUS_IGNORED,
):
    helm_rollback_command = [
        "helm",
        "rollback",
        package,
        "0",
    ]
    if dry_run:
        helm_rollback_command.append("--dry-run")

    await k8s.with_exec(helm_rollback_command)
    task_status.started()  # Release task lock
