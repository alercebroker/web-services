from core.domain.astroobject_model import AstroObject, Probability


def test_astroobject_model():
    dict_object = {
        "oid": "ZTF123",
        "ndethist": 1,
        "ncovhist": 1,
        "mjdstarthist": 1.0,
        "mjdendhist": 1.0,
        "corrected": False,
        "stellar": False,
        "ndet": 5,
        "g_r_max": 1.0,
        "g_r_max_corr": 1.0,
        "g_r_mean": 1.0,
        "g_r_mean_corr": 1.0,
        "meanra": 33.0,
        "meandec": 133.0,
        "sigmara": 3.0,
        "sigmadec": 1.0,
        "deltajd": 0.5,
        "firstmjd": 55555.0,
        "lastmjd": 555556.0,
        "step_id_corr": "asd",
        "diffpos": False,
        "reference_change": False,
    }

    aobj = AstroObject(**dict_object)
    assert aobj.oid == "ZTF123"
    assert aobj.ndet == 5
    assert aobj.probabilities == []


def test_probability_model():
    dict_object = {
        "oid": "ZTF123",
        "class_name": "SNIa",
        "classifier_name": "classifier",
        "classifier_version": "classifier_v1",
        "probability": 0.99,
        "ranking": 1,
    }

    prob = Probability(**dict_object)
    assert prob.oid == "ZTF123"
    assert prob.classifier_name == "classifier"
    assert prob.ranking == 1


def test_nested_models():
    dict_object = {
        "oid": "ZTF123",
        "ndethist": 1,
        "ncovhist": 1,
        "mjdstarthist": 1.0,
        "mjdendhist": 1.0,
        "corrected": False,
        "stellar": False,
        "ndet": 5,
        "g_r_max": 1.0,
        "g_r_max_corr": 1.0,
        "g_r_mean": 1.0,
        "g_r_mean_corr": 1.0,
        "meanra": 33.0,
        "meandec": 133.0,
        "sigmara": 3.0,
        "sigmadec": 1.0,
        "deltajd": 0.5,
        "firstmjd": 55555.0,
        "lastmjd": 555556.0,
        "step_id_corr": "asd",
        "diffpos": False,
        "reference_change": False,
        "probabilities": [
            {
                "oid": "ZTF123",
                "class_name": "SNIa",
                "classifier_name": "classifier",
                "classifier_version": "classifier_v1",
                "probability": 0.99,
                "ranking": 1,
            }
        ],
    }

    aobj = AstroObject(**dict_object)
    assert isinstance(aobj.probabilities[0], Probability)
