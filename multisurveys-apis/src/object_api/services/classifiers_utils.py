import re


def format_classifier_name(name):
    """
    Format the classifier name by replacing special characters with spaces and capitalizing each word.
    """

    name = re.sub(r'[$-/:-?{-~!"^_`]', " ", name)
    name = name.title()
    return name
