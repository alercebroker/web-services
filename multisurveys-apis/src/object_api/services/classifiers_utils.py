import re

ACRONYMS = {"atat", "bhrf", "lc", "lsst", "ztf"}


def format_classifier_name(name):
    """
    Format the classifier name: special characters become spaces, and each word is capitalized, except acronyms,
    which are uppercased.
    """

    words = re.sub(r'[$-/:-?{-~!"^_`]', " ", name).split()
    return " ".join(word.upper() if word.lower() in ACRONYMS else word.capitalize() for word in words)
