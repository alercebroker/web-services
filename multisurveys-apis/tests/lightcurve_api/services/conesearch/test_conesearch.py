from typing import Any
from db_plugins.db.sql.models import Object
from lightcurve_api.models.object import ApiObject
from lightcurve_api.services.conesearch import conesearch as conesearch_service
from numpy import int64


def implement_context_manager(mocker, mock):
    ctx_mock = mocker.MagicMock()
    ctx_mock.__enter__.return_value = mock
    ctx_mock.__exit__.return_value = False
    mock.return_value = ctx_mock


def database_mock(mocker, result=[], exception=None):
    mock = mocker.MagicMock()
    if exception is None:
        mock.execute.return_value.all.return_value = result
    else:
        mock.execute.side_effect = exception
    return mock


def test_conesearch_coordinates(mocker):
    # Setup the database mock
    # Result has to be a list of tuples
    # where the first element is the object
    mock = database_mock(
        mocker, [(Object(oid=123, meanra=45.0, meandec=45.0),)]
    )
    implement_context_manager(mocker, mock)

    # Call the service
    ra, dec, radius, neighbors = (45, 45, 30.0, 10)
    result = conesearch_service.conesearch_coordinates(
        ra, dec, radius, neighbors, mock
    )

    # Assert that the result is as expected
    assert result == [ApiObject(objectId="ZTF00aaaaaet", ra=45.0, dec=45.0)]
    mock.execute.assert_called_once()
    call_args = mock.execute.call_args[0]
    assert call_args[1] == {"ra": 45.0, "dec": 45.0, "radius": 30.0}


def test_conesearch_coordinates_db_empty(mocker):
    # Setup the database mock with empty result
    mock = database_mock(mocker, result=[])
    implement_context_manager(mocker, mock)

    # Call the service
    ra, dec, radius, neighbors = (45, 45, 30.0, 10)
    assert [] == conesearch_service.conesearch_coordinates(
        ra, dec, radius, neighbors, mock
    )


def test_conesearch_oid(mocker):
    # Setup the database mock
    # Result has to be a list of tuples
    # where the first element is the object
    mock = database_mock(
        mocker, [(Object(oid=123, meanra=45.0, meandec=45.0),)]
    )
    implement_context_manager(mocker, mock)

    # Call the service
    result = conesearch_service.conesearch_oid(int64(123), 30.0, 10, mock)

    # Assert that the result is as expected
    assert result == [ApiObject(objectId="ZTF00aaaaaet", ra=45.0, dec=45.0)]
    mock.execute.assert_called_once()
    call_args = mock.execute.call_args[0]
    assert call_args[1] == {"radius": 30.0}


def test_conesearch_oid_db_empty(mocker):
    # Setup the database mock with empty result
    mock = database_mock(mocker, result=[])
    implement_context_manager(mocker, mock)

    # Call the service
    result = conesearch_service.conesearch_oid(int64(123), 30.0, 10, mock)

    # Assert that the result is as expected
    assert result == []
    mock.execute.assert_called_once()
    call_args = mock.execute.call_args[0]
    assert call_args[1] == {"radius": 30.0}
    assert "123" == str(call_args[0].compile().params["oid_1"])


def test_conesearch_oid_lightcurve(mocker):
    # Setup the database mock

    mock = mocker.MagicMock()

    def execute_side_effect(*args, **_):
        # Check the SQL statement or parameters to determine what to return
        stmt = str(args[0])

        class wrapper:
            def __init__(self, data):
                self.data = data

            def all(self):
                return self.data

        if "q3c_radial_query" in stmt and "target.meanra" in stmt:
            # conesearch query
            return wrapper([(Object(oid=123, meanra=45.0, meandec=45.0),)])
        elif (
            "detection" in stmt.lower() and "non_detection" not in stmt.lower()
        ):
            # detections query
            return wrapper([(make_ztf_detection(123, 1, 1),)])
        elif "non_detection" in stmt.lower():
            # non-detections query
            return wrapper([(make_ztf_non_detection(123, 1),)])
        elif "forced" in stmt.lower() or "photometry" in stmt.lower():
            # forced photometry query
            return wrapper([(make_ztf_forced_photometry(123, 1),)])
        return wrapper(([],))

    mock.execute.side_effect = execute_side_effect
    implement_context_manager(mocker, mock)

    result = conesearch_service.conesearch_oid_lightcurve(
        "ZTF20aaelulu", 30.0, 10, "ZTF", mock
    )
    assert len(result.detections) == 1
    assert len(result.non_detections) == 1
    assert len(result.forced_photometry) == 1


class LightcurveWrapper:
    def __init__(self, *_, **kwargs):
        self.dict: dict[str, Any] = kwargs

    def __getattribute__(self, name):
        if name == "__dict__":
            return self.dict
        return super().__getattribute__(name)


def make_ztf_detection(oid, survey, measurement_id):
    return LightcurveWrapper(
        oid=oid,
        sid=survey,
        measurement_id=measurement_id,
        pid=12345,
        diffmaglim=20.5,
        isdiffpos=1,
        nid=67890,
        magpsf=19.8,
        sigmapsf=0.1,
        magap=19.9,
        sigmagap=0.12,
        distnr=1.5,
        rb=0.95,
        rbversion="v1.0",
        drb=0.92,
        drbversion="v1.0",
        magapbig=19.85,
        sigmagapbig=0.11,
        rfid=54321,
        magpsf_corr=19.75,
        sigmapsf_corr=0.09,
        sigmapsf_corr_ext=0.095,
        corrected=True,
        dubious=False,
        parent_candid=None,
        has_stamp=True,
        mjd=59000.5,
        ra=45.0,
        dec=45.0,
        band=1,
    )


def make_ztf_non_detection(oid, survey_id):
    return LightcurveWrapper(
        oid=oid,
        sid=survey_id,
        band=1,
        mjd=59000.5,
        diffmaglim=20.5,
    )


def make_ztf_forced_photometry(oid, survey_id):
    return LightcurveWrapper(
        oid=oid,
        sid=survey_id,
        measurement_id=123456,
        pid=78901,
        mag=19.5,
        e_mag=0.08,
        mag_corr=19.4,
        e_mag_corr=0.07,
        e_mag_corr_ext=0.075,
        isdiffpos=1,
        corrected=True,
        dubious=False,
        parent_candid=None,
        has_stamp=True,
        field=123,
        rcid=456,
        rfid=789,
        sciinpseeing=1.2,
        scibckgnd=100.5,
        scisigpix=5.0,
        magzpsci=26.5,
        magzpsciunc=0.1,
        magzpscirms=0.05,
        clrcoeff=0.1,
        clrcounc=0.05,
        exptime=30.0,
        adpctdif1=0.5,
        adpctdif2=0.3,
        diffmaglim=20.5,
        programid=1,
        procstatus="success",
        distnr=1.2,
        ranr=45.1,
        decnr=45.1,
        magnr=18.5,
        sigmagnr=0.2,
        chinr=1.1,
        sharpnr=0.05,
        mjd=59000.5,
        ra=45.0,
        dec=45.0,
        band=1,
    )
