from fixtures import client
from api.sql.probabilities.probabilities import Probabilities


def test_get_probabilities(psql_service, client):
    r = client.get("objects/ZTF1/probabilities")
    assert r.status_code == 200
    assert isinstance(r.json, list)


def test_get_probabilities_not_found(psql_service, client):
    r = client.get("objects/ZTF2/probabilities")
    assert r.status_code == 404


def test_order_probs():
    probs = [
        {
            "classifier_name": "lc_classifier",
            "class_name": "AGN",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "Blazar",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "CEP",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "CV/Nova",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "DSCT",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "E",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "LPV",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "Periodic-Other",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "QSO",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "RRL",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "SLSN",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "SNIa",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "SNIbc",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "SNII",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "YSO",
        },
        {
            "classifier_name": "lc_classifier_periodic",
            "class_name": "CEP",
        },
        {
            "classifier_name": "lc_classifier_periodic",
            "class_name": "DSCT",
        },
        {
            "classifier_name": "lc_classifier_periodic",
            "class_name": "E",
        },
        {
            "classifier_name": "lc_classifier_periodic",
            "class_name": "LPV",
        },
        {
            "classifier_name": "lc_classifier_periodic",
            "class_name": "Periodic-Other",
        },
        {
            "classifier_name": "lc_classifier_periodic",
            "class_name": "RRL",
        },
        {
            "classifier_name": "lc_classifier_stochastic",
            "class_name": "AGN",
        },
        {
            "classifier_name": "lc_classifier_stochastic",
            "class_name": "Blazar",
        },
        {
            "classifier_name": "lc_classifier_stochastic",
            "class_name": "CV/Nova",
        },
        {
            "classifier_name": "lc_classifier_stochastic",
            "class_name": "QSO",
        },
        {
            "classifier_name": "lc_classifier_stochastic",
            "class_name": "YSO",
        },
        {
            "classifier_name": "lc_classifier_top",
            "class_name": "Periodic",
        },
        {
            "classifier_name": "lc_classifier_top",
            "class_name": "Stochastic",
        },
        {
            "classifier_name": "lc_classifier_top",
            "class_name": "Transient",
        },
        {
            "classifier_name": "stamp_classifier",
            "class_name": "AGN",
        },
        {
            "classifier_name": "stamp_classifier",
            "class_name": "asteroid",
        },
        {
            "classifier_name": "stamp_classifier",
            "class_name": "bogus",
        },
        {
            "classifier_name": "stamp_classifier",
            "class_name": "SN",
        },
        {
            "classifier_name": "stamp_classifier",
            "class_name": "VS",
        },
    ]

    probabilities_resource = Probabilities()
    ordered = probabilities_resource.order_probs(probs)
    assert ordered == [
        {
            "classifier_name": "lc_classifier",
            "class_name": "SNIa",
        },
        {
            "classifier_name": "stamp_classifier",
            "class_name": "AGN",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "SNIbc",
        },
        {
            "classifier_name": "stamp_classifier",
            "class_name": "SN",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "SNII",
        },
        {
            "classifier_name": "stamp_classifier",
            "class_name": "VS",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "SLSN",
        },
        {
            "classifier_name": "stamp_classifier",
            "class_name": "asteroid",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "QSO",
        },
        {
            "classifier_name": "lc_classifier_stochastic",
            "class_name": "QSO",
        },
        {
            "classifier_name": "stamp_classifier",
            "class_name": "bogus",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "AGN",
        },
        {
            "classifier_name": "lc_classifier_stochastic",
            "class_name": "AGN",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "Blazar",
        },
        {
            "classifier_name": "lc_classifier_stochastic",
            "class_name": "Blazar",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "YSO",
        },
        {
            "classifier_name": "lc_classifier_stochastic",
            "class_name": "YSO",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "CV/Nova",
        },
        {
            "classifier_name": "lc_classifier_stochastic",
            "class_name": "CV/Nova",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "LPV",
        },
        {
            "classifier_name": "lc_classifier_periodic",
            "class_name": "LPV",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "E",
        },
        {
            "classifier_name": "lc_classifier_periodic",
            "class_name": "E",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "DSCT",
        },
        {
            "classifier_name": "lc_classifier_periodic",
            "class_name": "DSCT",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "RRL",
        },
        {
            "classifier_name": "lc_classifier_periodic",
            "class_name": "RRL",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "CEP",
        },
        {
            "classifier_name": "lc_classifier_periodic",
            "class_name": "CEP",
        },
        {
            "classifier_name": "lc_classifier",
            "class_name": "Periodic-Other",
        },
        {
            "classifier_name": "lc_classifier_periodic",
            "class_name": "Periodic-Other",
        },
        {
            "classifier_name": "lc_classifier_top",
            "class_name": "Periodic",
        },
        {
            "classifier_name": "lc_classifier_top",
            "class_name": "Transient",
        },
        {
            "classifier_name": "lc_classifier_top",
            "class_name": "Stochastic",
        },
    ]
