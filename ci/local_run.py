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
    "poetry run python main.py deploy add-package lightcurve --chart-folder=lightcurve_step2 --values=lightcurve-services-helm-values",
    "poetry run python main.py deploy execute staging --dry-run"
]

# Execute the commands
run_commands(commands)