import os

def run_commands(commands):
    for command in commands:
        print(f"Executing: {command}")
        status = os.system(command)
        if status != 0:
            print(f"Error executing '{command}'")

# List of Linux commands to execute
commands = [
    "poetry run python main.py deploy prepare",
    "poetry run python main.py deploy add-package lightcurve --chart-folder=lightcurve --values=lightcurve-service-helm-values",
    "poetry run python main.py deploy add-package ws-magstats --chart-folder=lightcurve --values=magstats-service-helm-values",
    "poetry run python main.py deploy add-package ws-object-details --chart-folder=lightcurve --values=object-details-service-helm-values",
    "poetry run python main.py deploy execute staging --dry-run"
]

commands_build = [
    "poetry run python main.py build prepare",
    "poetry run python main.py build add-package lightcurve lightcurve --chart-folder=lightcurve --chart-name=lightcurve",
    "poetry run python main.py build execute staging --dry-run"
]

commands_rollback = [
    "poetry run python main.py rollback prepare",
    "poetry run python main.py rollback add-package lightcurve --chart-folder=lightcurve --values=lightcurve-service-helm-values",
    "poetry run python main.py rollback add-package ws-magstats --chart-folder=lightcurve --values=magstats-service-helm-values",
    "poetry run python main.py rollback add-package ws-object-details --chart-folder=lightcurve --values=object-details-service-helm-values",
    "poetry run python main.py rollback execute staging --dry-run"
]

commands_test = [
    "poetry run python main.py rollback prepare",
    "poetry run python main.py rollback add-package lightcurve --chart-folder=lightcurve --values=lightcurve-service-helm-values",
    "poetry run python main.py rollback add-package ws-magstats --chart-folder=lightcurve --values=magstats-service-helm-values",
    "poetry run python main.py rollback add-package ws-object-details --chart-folder=lightcurve --values=object-details-service-helm-values",
    "poetry run python main.py rollback execute staging --dry-run"
]

# Execute the commands
run_commands(commands_build)