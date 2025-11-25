from core.repository.queries import detections as detection_repository
from core.repository.queries import non_detections as non_detection_repository
from core.repository.queries import (
    forced_photometry as forced_photometry_repository,
)
from db_plugins.db.sql.models import (
    Detection,
    ForcedPhotometry,
    ZtfDetection,
    Object,
    LsstDetection,
    ZtfForcedPhotometry,
    ZtfNonDetection,
)
from faker import Faker


def test_get_detections_by_list(db, faker: Faker):
    dets = []
    objects = [
        Object(
            oid=123,
            tid=1,
            sid=1,
            meanra=45.0,
            meandec=45.0,
            firstmjd=59000.0,
            lastmjd=59001.0,
            deltamjd=1.0,
            n_det=1,
            n_forced=1,
            n_non_det=1,
        ),
        Object(
            oid=456,
            tid=1,
            sid=1,
            meanra=45.0,
            meandec=45.0,
            firstmjd=59000.0,
            lastmjd=59001.0,
            deltamjd=1.0,
            n_det=1,
            n_forced=1,
            n_non_det=1,
        ),
        Object(
            oid=789,
            tid=0,
            sid=0,
            meanra=45.0,
            meandec=45.0,
            firstmjd=59000.0,
            lastmjd=59001.0,
            deltamjd=1.0,
            n_det=1,
            n_forced=1,
            n_non_det=1,
        ),
    ]
    with db.session() as session:
        for i in range(10):
            if i % 2 == 0:
                oid = 123
            else:
                oid = 456
            dets.append(
                Detection(
                    oid=oid,
                    sid=1,
                    measurement_id=i + 1,
                    mjd=59000.0,
                    ra=faker.latitude(),
                    dec=faker.longitude(),
                    band=1,
                )
            )
            dets.append(ZtfDetection(oid=oid, sid=1, measurement_id=i + 1))
        # have one additional detection from other survey
        dets.append(
            LsstDetection(
                oid=789,
                sid=0,
                measurement_id=11,
                visit=1,
                detector=1,
                x=1,
                y=1,
                timeProcessedMjdTai=1,
            )
        )

        session.add_all(objects)
        session.commit()
        session.add_all(dets)
        session.commit()

    rows, survey_id = detection_repository.get_detections_by_list(db.session)(
        ([123, 456], "ZTF")
    )
    result = [row[0] for row in rows]

    assert survey_id == "ZTF"
    assert len(result) == 10
    assert {row.oid for row in result} == {123, 456}


def test_get_detections_by_list_only_lsst(db):
    with db.session() as session:
        session.add(
            Object(
                oid=123,
                tid=0,
                sid=0,
                meanra=45.0,
                meandec=45.0,
                firstmjd=59000.0,
                lastmjd=59001.0,
                deltamjd=1.0,
                n_det=1,
                n_forced=1,
                n_non_det=1,
            )
        )
        for i in range(10):
            session.add(
                LsstDetection(
                    oid=123,
                    sid=0,
                    measurement_id=i + 1,
                    visit=i + 1,
                    detector=i + 1,
                    x=1,
                    y=1,
                    timeProcessedMjdTai=1,
                )
            )

    rows, survey_id = detection_repository.get_detections_by_list(db.session)(
        ([123, 456], "ZTF")
    )
    result = [row[0] for row in rows]

    assert survey_id == "ZTF"
    assert len(result) == 0


def test_get_non_detections_by_list(db, faker: Faker):
    with db.session() as session:
        session.add(
            Object(
                oid=123,
                tid=1,
                sid=1,
                meanra=45.0,
                meandec=45.0,
                firstmjd=59000.0,
                lastmjd=59001.0,
                deltamjd=1.0,
                n_det=1,
                n_forced=1,
                n_non_det=1,
            )
        )

        for _ in range(10):
            session.add(
                ZtfNonDetection(
                    oid=123,
                    sid=1,
                    band=1,
                    mjd=faker.unique.pyfloat(min_value=59000, max_value=60000),
                    diffmaglim=faker.pyfloat(min_value=20, max_value=25),
                )
            )

        session.commit()

    rows, survey_id = non_detection_repository.get_non_detections_by_list(db.session)(
        ([123], "ZTF")
    )
    result = [row[0] for row in rows]
    assert survey_id == "ZTF"
    assert len(result) == 10

    rows, survey_id = non_detection_repository.get_non_detections_by_list(db.session)(
        ([456], "ZTF")
    )
    result = [row[0] for row in rows]
    assert survey_id == "ZTF"
    assert len(result) == 0


def test_get_forced_photometry_by_list(db, faker: Faker):
    with db.session() as session:
        session.add(
            Object(
                oid=123,
                tid=1,
                sid=1,
                meanra=45.0,
                meandec=45.0,
                firstmjd=59000.0,
                lastmjd=59001.0,
                deltamjd=1.0,
                n_det=1,
                n_forced=1,
                n_non_det=1,
            )
        )

        for i in range(10):
            session.add(
                ForcedPhotometry(
                    oid=123,
                    sid=1,
                    measurement_id=i + 1,
                    mjd=59000.0,
                    ra=1,
                    dec=1,
                    band=1,
                )
            )
            session.add(
                ZtfForcedPhotometry(
                    oid=123,
                    sid=1,
                    measurement_id=i + 1,
                    mag=1,
                    e_mag=1,
                    isdiffpos=1,
                    corrected=True,
                    dubious=True,
                    has_stamp=True,
                    field=1,
                    rcid=1,
                    rfid=1,
                    sciinpseeing=1,
                    scibckgnd=1,
                    scisigpix=1,
                    magzpsci=1,
                    magzpsciunc=1,
                    magzpscirms=1,
                    clrcoeff=1,
                    clrcounc=1,
                    exptime=1,
                    adpctdif1=1,
                    adpctdif2=1,
                    diffmaglim=1,
                    programid=1,
                    procstatus="a",
                    distnr=1,
                    ranr=1,
                    decnr=1,
                    magnr=1,
                    sigmagnr=1,
                    chinr=1,
                    sharpnr=1,
                )
            )

        session.commit()

    rows, survey_id = forced_photometry_repository.get_forced_photometry_by_list(
        db.session
    )(([123], "ZTF"))
    result = [row[0] for row in rows]
    assert survey_id == "ZTF"
    assert len(result) == 10

    rows, survey_id = forced_photometry_repository.get_forced_photometry_by_list(
        db.session
    )(([456], "ZTF"))
    result = [row[0] for row in rows]
    assert survey_id == "ZTF"
    assert len(result) == 0
