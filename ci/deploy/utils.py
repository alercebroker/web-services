import os
import pathlib
import sys
import dagger

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


def prepare_k8s_container(client, cluster_name, cluster_alias):
    k8s_container = (
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
    )
    return k8s_container


def k8s_get_values(client: dagger.Client, k8s: dagger.Container, package: str):
    k8s.with_(
        get_values(
            client,
            str(pathlib.Path().cwd().parent.absolute()),
            f"{package}-service-helm-values",
        )
    )


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


async def helm_package(
    k8s: dagger.Container,
    package: str,
):
    helm_package_command = [
        "helm",
        "package",
        f"/web-services/charts/{package}/",
    ]

    await k8s.with_exec(helm_package_command)


async def helm_upgrade(
    k8s: dagger.Container,
    package: str,
    dry_run: bool,
):
    helm_upgrade_command = [
        "helm",
        "upgrade",
        "-i",
        "-f",
        "values.yaml",
        package,
        f"web-services/{package}",
    ]
    if dry_run:
        helm_upgrade_command.append("--dry-run")

    await k8s.with_exec(helm_upgrade_command)


async def helm_rollback(
    k8s: dagger.Container,
    package: str,
    dry_run: bool,
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
