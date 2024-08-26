import os
import pathlib
import sys
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
    values_names_dict = {
        "lightcurve": "lightcurve-service-helm-values",
        "magstats": "magstats-service-helm-values",
        "object-details": "object-details-service-helm-values",
    }
    package_values = values_names_dict[package] if package in values_names_dict.keys() else package

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
                package_values,
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


def helm_package(
    k8s: dagger.Container,
    package: str,
):
    chart_names_dict = {
        "lightcurve": "lightcurve",
        "magstats": "lightcurve",
        "object-details": "lightcurve",
    }

    package_chart = chart_names_dict[package] if package in chart_names_dict.keys() else package,

    helm_package_command = [
        "helm",
        "package",
        f"/web-services/charts/{package_chart}/",
    ]
    k8s = k8s.with_exec(helm_package_command)
    return k8s


def helm_upgrade(
    k8s: dagger.Container,
    package: str,
    dry_run: bool,
    from_repo: bool = False,
):
    
    chart_names_dict = {
        "lightcurve": "lightcurve",
        "magstats": "lightcurve",
        "object-details": "lightcurve",
    }

    package_chart = chart_names_dict[package] if package in chart_names_dict.keys() else package,

    version = current_chart_version(package)
    helm_upgrade_command = [
        "helm",
        "upgrade",
        "-i",
        "-f",
        "values.yaml",
        package,
    ]
    if from_repo:
        helm_upgrade_command.append(f"web-services/{package_chart}")
    else:
        helm_upgrade_command.append(
            f"/web-services/ci/{package_chart}-{version}.tgz"
        )
    if dry_run:
        helm_upgrade_command.append("--dry-run")

    k8s = k8s.with_exec(helm_upgrade_command)
    return k8s


def helm_rollback(
    k8s: dagger.Container,
    package: str,
    dry_run: bool,
):
    chart_names_dict = {
        "lightcurve": "lightcurve",
        "magstats": "lightcurve",
        "object-details": "lightcurve",
    }

    package_chart = chart_names_dict[package] if package in chart_names_dict.keys() else package,

    helm_rollback_command = [
        "helm",
        "rollback",
        package_chart,
        "0",
    ]
    if dry_run:
        helm_rollback_command.append("--dry-run")

    k8s = k8s.with_exec(helm_rollback_command)
    return k8s
