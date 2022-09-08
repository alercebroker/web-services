import requests
from .token_builder import BASE_URL


def get_all_features(aid):
    return requests.get(f"{BASE_URL}/objects/{aid}/features")


def get_all_features_with_fid(aid, fid):
    return requests.get(f"{BASE_URL}/objects/{aid}/features?fid={fid}")


def get_all_features_with_version(aid, version):
    return requests.get(f"{BASE_URL}/objects/{aid}/features?version={version}")


def get_all_features_with_fid_and_version(aid, fid, version):
    return requests.get(f"{BASE_URL}/objects/{aid}/features?fid={fid}&version={version}")


def get_feature(aid, feature_name):
    return requests.get(f"{BASE_URL}/objects/{aid}/features/{feature_name}")


def get_feature_with_fid(aid, feature_name, fid):
    return requests.get(f"{BASE_URL}/objects/{aid}/features/{feature_name}?fid={fid}")


def get_feature_with_version(aid, feature_name, version):
    return requests.get(f"{BASE_URL}/objects/{aid}/features/{feature_name}?version={version}")


def get_feature_with_fid_and_version(aid, feature_name, fid, version):
    return requests.get(f"{BASE_URL}/objects/{aid}/features/{feature_name}?fid={fid}&version={version}")
