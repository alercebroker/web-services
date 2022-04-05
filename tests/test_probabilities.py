from api.resources.probabilities.probabilities import Probabilities
from db_plugins.db.sql.models import Probability, Taxonomy

taxonomy = [
    Taxonomy(
        classifier_name="lc_classifier",
        classes=[
            "SNIa",
            "SNIbc",
            "SNII",
            "SLSN",
            "QSO",
            "AGN",
            "Blazar",
            "CV/Nova",
            "YSO",
            "LPV",
            "E",
            "DSCT",
            "RRL",
            "CEP",
            "Periodic-Other",
        ],
    ),
    Taxonomy(
        classifier_name="lc_classifier_top",
        classes=["Transient", "Stochastic", "Periodic"],
    ),
    Taxonomy(
        classifier_name="lc_classifier_transient",
        classes=["SNIa", "SNIbc", "SNII", "SLSN"],
    ),
    Taxonomy(
        classifier_name="lc_classifier_stochastic",
        classes=["QSO", "AGN", "Blazar", "CV/Nova", "YSO"],
    ),
    Taxonomy(
        classifier_name="lc_classifier_periodic",
        classes=["LPV", "E", "DSCT", "RRL", "CEP", "Periodic-Other"],
    ),
    Taxonomy(
        classifier_name="stamp_classifier",
        classes=["NS", "ANG", "SV", "dioretsa", "sugob"],
    ),
    Taxonomy(
        classifier_name="stamp_classifier",
        classes=["SN", "AGN", "VS", "asteroid", "bogus"],
    ),
]


def test_get_probabilities(psql_service, client):
    r = client.get("objects/ZTF1/probabilities")
    assert r.status_code == 200
    assert isinstance(r.json, list)


def test_get_probabilities_not_found(psql_service, client):
    r = client.get("objects/ZTF2/probabilities")
    assert r.status_code == 404


def test_order_probs():
    probs = [
        Probability(classifier_name="lc_classifier", class_name="AGN"),
        Probability(classifier_name="lc_classifier", class_name="Blazar"),
        Probability(classifier_name="lc_classifier", class_name="CEP"),
        Probability(classifier_name="lc_classifier", class_name="CV/Nova"),
        Probability(classifier_name="lc_classifier", class_name="DSCT"),
        Probability(classifier_name="lc_classifier", class_name="E"),
        Probability(classifier_name="lc_classifier", class_name="LPV"),
        Probability(
            classifier_name="lc_classifier", class_name="Periodic-Other"
        ),
        Probability(classifier_name="lc_classifier", class_name="QSO"),
        Probability(classifier_name="lc_classifier", class_name="RRL"),
        Probability(classifier_name="lc_classifier", class_name="SLSN"),
        Probability(classifier_name="lc_classifier", class_name="SNIa"),
        Probability(classifier_name="lc_classifier", class_name="SNIbc"),
        Probability(classifier_name="lc_classifier", class_name="SNII"),
        Probability(classifier_name="lc_classifier", class_name="YSO"),
        Probability(
            classifier_name="lc_classifier_periodic", class_name="CEP"
        ),
        Probability(
            classifier_name="lc_classifier_periodic", class_name="DSCT"
        ),
        Probability(classifier_name="lc_classifier_periodic", class_name="E"),
        Probability(
            classifier_name="lc_classifier_periodic", class_name="LPV"
        ),
        Probability(
            classifier_name="lc_classifier_periodic",
            class_name="Periodic-Other",
        ),
        Probability(
            classifier_name="lc_classifier_periodic", class_name="RRL"
        ),
        Probability(
            classifier_name="lc_classifier_stochastic", class_name="AGN"
        ),
        Probability(
            classifier_name="lc_classifier_stochastic", class_name="Blazar"
        ),
        Probability(
            classifier_name="lc_classifier_stochastic", class_name="CV/Nova"
        ),
        Probability(
            classifier_name="lc_classifier_stochastic", class_name="QSO"
        ),
        Probability(
            classifier_name="lc_classifier_stochastic", class_name="YSO"
        ),
        Probability(
            classifier_name="lc_classifier_top", class_name="Periodic"
        ),
        Probability(
            classifier_name="lc_classifier_top", class_name="Stochastic"
        ),
        Probability(
            classifier_name="lc_classifier_top", class_name="Transient"
        ),
        Probability(classifier_name="stamp_classifier", class_name="AGN"),
        Probability(classifier_name="stamp_classifier", class_name="asteroid"),
        Probability(classifier_name="stamp_classifier", class_name="bogus"),
        Probability(classifier_name="stamp_classifier", class_name="SN"),
        Probability(classifier_name="stamp_classifier", class_name="VS"),
    ]

    probabilities_resource = Probabilities()
    ordered = probabilities_resource.order_probs(probs, taxonomy)
    expected = [
        Probability(classifier_name="lc_classifier", class_name="SNIa"),
        Probability(
            classifier_name="lc_classifier_periodic", class_name="LPV"
        ),
        Probability(
            classifier_name="lc_classifier_stochastic", class_name="QSO"
        ),
        Probability(
            classifier_name="lc_classifier_top", class_name="Transient"
        ),
        Probability(classifier_name="stamp_classifier", class_name="SN"),
        Probability(classifier_name="lc_classifier", class_name="SNIbc"),
        Probability(classifier_name="lc_classifier_periodic", class_name="E"),
        Probability(
            classifier_name="lc_classifier_stochastic", class_name="AGN"
        ),
        Probability(
            classifier_name="lc_classifier_top", class_name="Stochastic"
        ),
        Probability(classifier_name="stamp_classifier", class_name="AGN"),
        Probability(classifier_name="lc_classifier", class_name="SNII"),
        Probability(
            classifier_name="lc_classifier_periodic", class_name="DSCT"
        ),
        Probability(
            classifier_name="lc_classifier_stochastic", class_name="Blazar"
        ),
        Probability(
            classifier_name="lc_classifier_top", class_name="Periodic"
        ),
        Probability(classifier_name="stamp_classifier", class_name="VS"),
        Probability(classifier_name="lc_classifier", class_name="SLSN"),
        Probability(
            classifier_name="lc_classifier_periodic", class_name="RRL"
        ),
        Probability(
            classifier_name="lc_classifier_stochastic", class_name="CV/Nova"
        ),
        Probability(classifier_name="stamp_classifier", class_name="asteroid"),
        Probability(classifier_name="lc_classifier", class_name="QSO"),
        Probability(
            classifier_name="lc_classifier_periodic", class_name="CEP"
        ),
        Probability(
            classifier_name="lc_classifier_stochastic", class_name="YSO"
        ),
        Probability(classifier_name="stamp_classifier", class_name="bogus"),
        Probability(classifier_name="lc_classifier", class_name="AGN"),
        Probability(
            classifier_name="lc_classifier_periodic",
            class_name="Periodic-Other",
        ),
        Probability(classifier_name="lc_classifier", class_name="Blazar"),
        Probability(classifier_name="lc_classifier", class_name="CV/Nova"),
        Probability(classifier_name="lc_classifier", class_name="YSO"),
        Probability(classifier_name="lc_classifier", class_name="LPV"),
        Probability(classifier_name="lc_classifier", class_name="E"),
        Probability(classifier_name="lc_classifier", class_name="DSCT"),
        Probability(classifier_name="lc_classifier", class_name="RRL"),
        Probability(classifier_name="lc_classifier", class_name="CEP"),
        Probability(
            classifier_name="lc_classifier", class_name="Periodic-Other"
        ),
    ]

    for i, proba in enumerate(ordered):
        assert proba.class_name == expected[i].class_name
        assert proba.classifier_name == expected[i].classifier_name
