from anomaly_api.database.alerts_queries import get_objects_by_oid, get_object_list, ProbabilityFilter
from anomaly_api.database.score_queries import get_objects_by_score, get_scores_by_oid, get_scores_distributions

# Pruebas alertas
LIST_OID = [
    "ZTF18abjmnnc",
    "ZTF19ablpmke",
    "ZTF18admaypn",
    "ZTF21abqvrbv",
    "ZTF19abiqomg",
    "ZTF20aboelxh",
    "ZTF19abcekit"
]
result1 = get_objects_by_oid(LIST_OID)

print(f"Result 1\n------ \n with oids {LIST_OID} \n {result1}\n------")

MIN_DET = 50
MAX_DET = 52

result2 = get_object_list(MIN_DET, MAX_DET)
print(f"Result 2\n------ \n with ndet between {MIN_DET} and {MAX_DET} \n {result2}\n------")


CLASSIFIER_NAME = "stamp_classifier"
CLASS_NAME = "SN"
PROBABILITY = 0.1

P_FILTER = ProbabilityFilter(CLASSIFIER_NAME, CLASS_NAME, PROBABILITY - 0.5, PROBABILITY + 0.5)

result3 = get_object_list(MIN_DET, MAX_DET, P_FILTER)
print(f"Result 3\n------ \n with ndet between {MIN_DET} and {MAX_DET} \n {result3}\n------")

# Pruebas score

OIDS = [
    "ZTF18abtourj",
    "ZTF18abuagmb",
    "ZTF18abtmxvh"
]

result4 = get_scores_by_oid(OIDS)

print(f"Result 4\n------ \n with oids {OIDS} \n {result4}\n------")

FILTER_LIST = [
    {
        "category": "Periodic",
        "min_score": 6.211925888061523,
        "max_score": 6.311925888061523
    },
    {
        "category": "Transient",
        "min_score": 0.4534198546409607,
        "max_score": 0.4734198546409607
    },
]

result5 = get_objects_by_score(FILTER_LIST)

print(f"Result 5\n------ \n with oids {FILTER_LIST} \n {result5}\n------")

CATEGORIES_LIST = [
    "Periodic",
    "Stochastic"
]

result6 = get_scores_distributions(CATEGORIES_LIST)

print(f"Result 6\n------ \n with oids {CATEGORIES_LIST} \n {result6}\n------")




#min_dets=50&max_dets=10&classifier_name=lc_classifier&class_name=SNIa&min_probability=0.5&max_probability=0.8&score_query=(Transient,0.6,0.8)