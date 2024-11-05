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
    "poetry run python main.py deploy add-package ws-magstats --chart-folder=ws-magstats --values=magstats-service-helm-values",
    "poetry run python main.py deploy execute staging --dry-run"
]

commands_build = [
    "poetry run python main.py build prepare",
    "poetry run python main.py build add-package lightcurve lightcurve --chart-folder=lightcurve --chart-name=lightcurve",
    "poetry run python main.py build execute staging --dry-run"
]

# Execute the commands
run_commands(commands)