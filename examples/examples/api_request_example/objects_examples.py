import requests
from .token_builder import BASE_URL


def get_single_object(aid):
    return requests.get(f"{BASE_URL}/objects/{aid}")


def get_limits():
    return requests.get(f"{BASE_URL}/objects/limit_values")


def get_objects_by_identifiers(*ids):
    return requests.get(f"{BASE_URL}/objects?oid={'&oid='.join(ids)}")


def get_objects_with_conesearch(ra, dec, radius):
    return requests.get(f"{BASE_URL}/objects?ra={ra}&dec={dec}&radius={radius}")


def get_objects_in_range_of_ndet(min_ndet, max_ndet):
    return requests.get(f"{BASE_URL}/objects?ndet={min_ndet}&ndet={max_ndet}")


def get_objects_in_range_of_first_mjd(min_firstmjd, max_firstmjd):
    return requests.get(f"{BASE_URL}/objects?firstmjd={min_firstmjd}&firstmjd={max_firstmjd}")


def get_objects_in_range_of_last_mjd(min_lastmjd, max_lastmjd):
    return requests.get(f"{BASE_URL}/objects?lastmjd={min_lastmjd}&lastmjd={max_lastmjd}")


def get_objects_by_classifier(classifier_name):
    return requests.get(f"{BASE_URL}/objects?classifier={classifier_name}")


def get_objects_by_ranking(ranking):
    return requests.get(f"{BASE_URL}/objects?ranking={ranking}")


def get_objects_by_probability(probability):
    return requests.get(f"{BASE_URL}/objects?probability={probability}")


def get_objects_by_class(class_name):
    return requests.get(f"{BASE_URL}/objects?class={class_name}")


def get_objects_by_classifier_version(classifier_version):
    return requests.get(f"{BASE_URL}/objects?classifier_version={classifier_version}")


def get_objects_sorted_by_probability_ascending():
    return requests.get(f"{BASE_URL}/objects?order_by=probability&order_mode=ASC")


def get_objects_sorted_by_probability_descending():
    return requests.get(f"{BASE_URL}/objects?order_by=probability&order_mode=DESC")


def get_objects_sorted_by_number_of_detections_ascending():
    return requests.get(f"{BASE_URL}/objects?order_by=ndet&order_mode=ASC")


def get_objects_sorted_by_number_of_detections_descending():
    return requests.get(f"{BASE_URL}/objects?order_by=ndet&order_mode=DESC")


def get_objects_sorted_by_first_detection_date_ascending():
    return requests.get(f"{BASE_URL}/objects?order_by=firstmjd&order_mode=ASC")


def get_objects_sorted_by_first_detection_date_descending():
    return requests.get(f"{BASE_URL}/objects?order_by=firstmjd&order_mode=DESC")


def get_objects_sorted_by_last_detection_date_ascending():
    return requests.get(f"{BASE_URL}/objects?order_by=lastmjd&order_mode=ASC")


def get_objects_sorted_by_last_detection_date_descending():
    return requests.get(f"{BASE_URL}/objects?order_by=lastmjd&order_mode=DESC")
