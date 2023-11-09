import sys
import re
import dagger
import pathlib


def current_chart_version(package: str, version: str = ""):
    with open(f"../charts/{package}/Chart.yaml", "r+") as f:
        original = f.read()
        f.seek(0)
        match = re.search(
            r"version: (?P<version>(\d+).(\d+).(\d+).*)", original
        )
        if not match:
            raise ValueError("Could not find valid version in Chart.yaml")
        version = version or match.group("version")

    return version


async def get_poetry_version(package_dir: str) -> list:
    config = dagger.Config(log_output=sys.stdout)

    async with dagger.Connection(config) as client:
        path = pathlib.Path().cwd().parent.absolute()
        # get build context directory
        source = (
            client.container()
            .from_("python:3.11-slim")
            .with_exec(["pip", "install", "poetry"])
            .with_directory(
                "/web-services",
                client.host().directory(
                    str(path), exclude=[".venv/", "**/.venv/"]
                ),
            )
        )

        runner = source.with_workdir(f"/web-services/{package_dir}").with_exec(
            ["poetry", "version", "--short"]
        )

        out = await runner.stdout()

    return ["rc", out.strip("\n")]


def set_environment(envs: dict[str, str]):
    def env_variables_inner(ctr: dagger.Container):
        for key, value in envs.items():
            ctr = ctr.with_env_variable(key, value)
        return ctr

    return env_variables_inner


if __name__ == "__main__":
    import anyio

    packages = ["lightcurve", "astroobject"]

    chart_versions = {}
    for package in packages:
        chart_versions[package] = anyio.run(current_chart_version, package)

    poetry_versions = {}
    for package in packages:
        poetry_versions[package] = anyio.run(get_poetry_version, package)

    for package, chart_version in chart_versions.items():
        print(f"Chart version {package}: {chart_version}")
    
    for package, poetry_version in poetry_versions.items():
        print(f"Poetry version {package}: {poetry_version}")