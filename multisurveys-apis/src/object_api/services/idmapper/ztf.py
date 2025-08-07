import numpy as np


def encode_ztf_to_masterid_without_survey(ztf_oid: str, validate: bool) -> np.int64:
    if not isinstance(ztf_oid, str):
        raise ValueError(f"Invalid ZTF object ID: {ztf_oid}")
    if validate and not is_ztf_oid_valid(ztf_oid):
        raise ValueError(f"Invalid ZTF object ID: {ztf_oid}")

    year = ztf_oid[3:5]
    seq = ztf_oid[5:12]

    # Convert the sequence of letters to a number
    master_id = 0
    for i, char in enumerate(seq):
        master_id += (ord(char) - ord("a")) * (26 ** (6 - i))

    # Convert the year to a number and add it to the master ID
    master_id += int(year) * 26**7
    return master_id

def is_ztf_oid_valid(ztf_oid: str) -> bool:
    """
    Checks that ztf_oid starts with ZTF, then two numbers and
    finally a sequence of 7 lowercase letters between a and z.

    :param ztf_oid: The ZTF object ID to validate.
    :return: True if ztf_oid is valid, False otherwise
    """
    if not isinstance(ztf_oid, str):
        return False
    if len(ztf_oid) != 12:
        return False
    if ztf_oid[0:3] != "ZTF":
        return False
    if not ztf_oid[3:5].isdigit():
        return False
    if not ztf_oid[5:12].isalpha():
        return False
    if not ztf_oid[5:12].islower():
        return False
    return True