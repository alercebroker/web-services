import pytest

from object_api.services.classifiers_utils import format_classifier_name


@pytest.mark.parametrize(
    "name, label",
    [
        ("lc_classifier_BHRF_forced_phot", "LC Classifier BHRF Forced Phot"),
        ("lc_classifier_BHRF_forced_phot_periodic", "LC Classifier BHRF Forced Phot Periodic"),
        ("stamp_classifier", "Stamp Classifier"),
        ("stamp_classifier_2025_beta", "Stamp Classifier 2025 Beta"),
        ("stamp_classifier_rubin_beta_20260421", "Stamp Classifier Rubin Beta 20260421"),
        ("lc_classifier_ATAT (beta)", "LC Classifier ATAT Beta"),
        ("stamp_classifier_ztf", "Stamp Classifier ZTF"),
        ("atatürk_classifier", "Atatürk Classifier"),
    ],
)
def test_classifier_labels(name, label):
    assert format_classifier_name(name) == label
