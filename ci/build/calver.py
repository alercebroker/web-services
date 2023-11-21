import datetime


def get_micro_from_dash(micro_and_modifier: str):
    micro = micro_and_modifier.split("-")[0]
    try:
        modifier = micro_and_modifier.split("-")[1]
    except IndexError:
        modifier = ""
    return micro, modifier


def get_micro_from_a(micro_and_modifier: str):
    micro = micro_and_modifier.split("a")[0]
    try:
        modifier = micro_and_modifier.split("a")[1]
    except IndexError:
        modifier = ""
    return micro, modifier


def get_calver(current_version: str, version_from_command: str):
    major = str(datetime.datetime.now().year)[2:]
    minor = datetime.datetime.now().month
    micro_and_modifier = current_version.split(".")[2]
    if "-" in micro_and_modifier:
        micro, modifier = get_micro_from_dash(micro_and_modifier)
    elif "a" in micro_and_modifier:
        micro, modifier = get_micro_from_a(micro_and_modifier)
    elif micro_and_modifier.isdigit():
        micro = micro_and_modifier
        modifier = ""
    else:
        raise ValueError("Could not parse micro and modifier")
    if version_from_command == "prerelease":
        try:
            modifier = f"-rc{int(modifier[2:]) + 1}"
        except ValueError:
            modifier = "-rc1"
    else:
        modifier = ""
        micro = int(micro) + 1
    return f"{major}.{minor}.{micro}{modifier}"
