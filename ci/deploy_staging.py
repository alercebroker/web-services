import dagger
import os
import sys
import anyio
import pathlib
from multiprocessing import Process


def secret_variables(envs: dict[str, str], client: dagger.Client):
    def env_variables_inner(ctr: dagger.Container):
        for key, value in envs.items():
            secret = client.set_secret(key, value)
            ctr = ctr.with_secret_variable(key, secret)
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
            .with_exec(["pip", "install", "poetry"])
            .with_exec(["poetry", "install"])
            .with_exec(
                [
                    "poetry",
                    "run",
                    "python",
                    "ssm.py",
                    ssm_parameter_name,
                ]
            )
        )
        return ctr

    return get_values_inner


async def helm_upgrade(package: str, dry_run: bool):
    config = dagger.Config(log_output=sys.stdout)

    async with dagger.Connection(config) as client:
        k8s = (
            client.container()
            .from_("alpine/k8s:1.24.16")
            .with_(
                secret_variables(
                    {
                        "AWS_ACCESS_KEY_ID": os.environ["AWS_ACCESS_KEY_ID"],
                        "AWS_SECRET_ACCESS_KEY": os.environ[
                            "AWS_SECRET_ACCESS_KEY"
                        ],
                        "AWS_SESSION_TOKEN": os.environ["AWS_SESSION_TOKEN"],
                    },
                    client,
                )
            )
            .with_env_variable(
                "AWS_DEFAULT_REGION", os.environ["AWS_DEFAULT_REGION"]
            )
            .with_exec(
                [
                    "aws",
                    "eks",
                    "update-kubeconfig",
                    "--region",
                    "us-east-1",
                    "--name",
                    "staging",
                    "--alias",
                    "staging",
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
            .with_exec(["kubectl", "config", "use-context", "staging"])
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


def deploy_package(package: str, dry_run: bool):
    print(f"Deploying {package}")
    anyio.run(helm_upgrade, package, dry_run)


def deploy_staging(dry_run: bool):
    packages = ["lightcurve", "astroobject"]
    for package in packages:
        p = Process(target=deploy_package, args=[package, dry_run])
        p.start()