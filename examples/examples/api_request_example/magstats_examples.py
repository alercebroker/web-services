import requests
from .token_builder import BASE_URL


def get_all_magstats(aid):
    return requests.get(f"{BASE_URL}/objects/{aid}/magstats")
