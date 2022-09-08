import requests
from .token_builder import BASE_URL


def get_all_classifiers():
    return requests.get(f"{BASE_URL}/classifiers")


def get_all_classes(classifier_name, classifier_version):
    return requests.get(f"{BASE_URL}/classifiers/{classifier_name}/{classifier_version}/classes")
