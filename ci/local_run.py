import os

def run_commands(commands):
    for command in commands:
        print(f"Executing: {command}")
        status = os.system(command)
        if status != 0:
            print(f"Error executing '{command}'")

# List of Linux commands to execute
commands = [
    "poetry run python main.py prepare",
    "poetry run python main.py add-package lightcurve --chart-folder=lightcurve_step --values=lightcurve-helm-values --chart=test1",
    "poetry run python main.py add-package magstats --chart-folder=test1 --values=test-helm --chart=test2",
    "poetry run python main.py execute deploy staging --dry-run"
]

# Execute the commands
run_commands(commands)