import requests
from .token_builder import BASE_URL


def get_all_probabilities(aid):
    return requests.get(f"{BASE_URL}/objects/{aid}/probabilities")


def get_all_probabilities_with_classifier(aid, classifier_name):
    return requests.get(f"{BASE_URL}/objects/{aid}/probabilities?classifier={classifier_name}")


def get_all_probabilities_with_classifier_and_version(aid, classifier_name, classifier_version):
    return requests.get(f"{BASE_URL}/objects/{aid}/probabilities?classifier={classifier_name}&classifier_version={classifier_version}")
