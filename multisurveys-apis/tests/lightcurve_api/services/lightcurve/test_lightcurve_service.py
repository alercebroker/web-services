from lightcurve_api.services import lightcurve_service
from db_plugins.db.sql._connection import PsqlDatabase
from conftest import _generate_lsst_detection


def test_get_detections_by_list(
    populate_database, db_setup: PsqlDatabase, faker
):
    populate_database(100)

    with db_setup.session() as session:
        for i in range(100):
            detection, lsst_detection = _generate_lsst_detection(
                faker, 1234, i
            )
            session.add(detection)
            session.add(lsst_detection)
            session.commit()

    result = lightcurve_service.get_detections_by_list(
        ["1234"], "LSST", db_setup.session
    )

    assert len(result) >= 100
