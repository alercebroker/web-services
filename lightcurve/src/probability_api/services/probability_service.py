from contextlib import AbstractContextManager
from typing import Callable
from sqlalchemy.orm import Session
from core.exceptions import DatabaseError, ObjectNotFound
from core.repository.queries.probability import _query_probabilities_sql
from core.repository.queries.taxonomy import _query_taxonomies_sql
from ..models.probability import Probability as ProbabilityModel
from ..models.taxonomy import Taxonomy as TaxonomyModel

def get_probabilities(
    oid: str, session_factory: Callable[..., AbstractContextManager[Session]]
) -> list:
    try:

        prob_list = _query_probabilities_sql(oid=oid, session_factory=session_factory)

        get_prob_data = [row[0] for row in prob_list]
        get_prob_list = []
        
        for prob in get_prob_data:
            get_prob_list.append(ProbabilityModel(**prob.__dict__))
        
        if prob_list is None:
            raise ObjectNotFound(oid)
        
        return get_prob_list
    except ObjectNotFound:
        raise


def get_taxonomies(
    session_factory: Callable[..., AbstractContextManager[Session]],
) -> list:
    try:

        taxonomy_list = _query_taxonomies_sql(session_factory=session_factory)

        get_taxonomy_data = [row[0] for row in taxonomy_list]
        get_taxonomy_list = []
        
        for prob in get_taxonomy_data:
            get_taxonomy_list.append(TaxonomyModel(**prob.__dict__))
        
        return get_taxonomy_list
    except ObjectNotFound:
        raise


def taxonomy_data(taxonomy_list):
    """
        dict example: {classifier_name:{class_name:[],classifier_version:''}}
    """
    
    taxonomy_dict  = {}

    for n in range(len(taxonomy_list)):
        taxonomy_dict[taxonomy_list[n].classifier_name] = taxonomy_list[n].__dict__

    return taxonomy_dict


def filter_data_by_higher_version(prob_dict):

    """
        Dictionary format: {'classifier_name': {'classifier_version: [{},{},{}]}}
    """
    data_by_higher_version = {}

    for itemKey, itemValue in prob_dict.items():
        if len(itemValue) > 1 :
            lastest_version = max(itemValue.keys())
            if itemKey not in data_by_higher_version:
                data_by_higher_version[itemKey] = {lastest_version: itemValue[lastest_version]}
        else: 
            if itemKey not in data_by_higher_version:
                data_by_higher_version[itemKey] = itemValue

    return data_by_higher_version

    
def group_data_by_classifier_dict(prob_lis):
    group_data_by_classifier = {}

    for item in prob_lis:
        aux_dict = {
        'classifier_name': item.classifier_name,
        'classifier_version': item.classifier_version,
        'class_name': item.class_name,
        'probability': item.probability,
        'ranking': item.ranking,
        }
        classifier_name = item.classifier_name
        classifier_version = item.classifier_version

        if item.classifier_name not in group_data_by_classifier:
            group_data_by_classifier[classifier_name] = {}
        
        if classifier_version not in group_data_by_classifier[classifier_name]:
            group_data_by_classifier[classifier_name][classifier_version]= []

        group_data_by_classifier[classifier_name][classifier_version].append(aux_dict)

    return group_data_by_classifier

def classifiers_options(group_prob_by_version):
    class_dict = []
    priorities = {
    'lc_classifier': 0,
    'lc_classifier_top': 1,
    'stamp_classifier': 2,
    'LC_classifier_ATAT_forced_phot(beta)': 3,
    'LC_classifier_BHRF_forced_phot(beta)': 4,
    }

    for key, value in priorities.items():
        if key in group_prob_by_version:
            class_dict.append({ key : format_classifiers_name(key) })

    return class_dict

def format_classifiers_name(classifier_name):
    classifier_name = classifier_name.replace('_',' ').title()

    if classifier_name.find('Atat') != -1:
        classifier_name = classifier_name.replace("Atat", "ATAT")
    if classifier_name.find('Bhrf') != -1:
        classifier_name = classifier_name.replace("Bhrf", "BHRF")

    return classifier_name
