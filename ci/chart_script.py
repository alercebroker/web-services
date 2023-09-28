import re
import sys


def update_app_version(package: str, new_version: str, dry_run: bool):
    with open(f"../charts/{package}/Chart.yaml", "r+") as f:
        original = f.read()
        f.seek(0)
        chart = re.sub(
            r"appVersion: (\d+).(\d+).(\d+).*",
            f"appVersion: {new_version}",
            original,
        )
        if not dry_run:
            f.write(chart)


def update_chart_version(
    package: str, version: str = "", dry_run: bool = False
):
    with open(f"../charts/{package}/Chart.yaml", "r+") as f:
        original = f.read()
        f.seek(0)
        match = re.search(
            r"version: (?P<version>(\d+).(\d+).(\d+).*)", original
        )
        if not match:
            raise ValueError("Could not find valid version in Chart.yaml")
        version = version or match.group("version")
        major, minor, patch = version.split(".")
        chart = re.sub(
            r"version: (\d+).(\d+).(\d+.*)",
            f"version: { major }.{ minor }.{ int(patch) + 1 }",
            original,
        )
        if not dry_run:
            f.write(chart)


def get_package_version(package: str):
    with open(f"../{package}/pyproject.toml", "r") as f:
        pyproject = f.read()
        poetry_section = re.search(
            r"\[tool\.poetry\]([\s\S]*?)\n\[[^\[\]]+\]|\[tool\.poetry\]([\s\S]*?)$",
            pyproject,
        )
        if not poetry_section:
            raise ValueError("Could not find poetry section in pyproject.toml")
        section = poetry_section.group(1)
        match = re.search(
            r'version = "(?P<version>(\d+).(\d+).(\d+).*)"', section
        )
        if not match:
            raise ValueError("Could not find version in pyproject.toml")
        version = match.group("version")
        return version


def main(package: str, dry_run: bool):
    package_version = get_package_version(package)
    update_app_version(package, package_version, dry_run)
    update_chart_version(package, dry_run=dry_run)


if __name__ == "__main__":
    package = sys.argv[1]
    dry_run = False
    if len(sys.argv) > 2:
        dry_run = sys.argv[2] == "--dry-run"
    main(package, dry_run)
