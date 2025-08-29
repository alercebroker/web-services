from db_plugins.db.sql.models import Object
from lightcurve_api.models.object import ApiObject
from lightcurve_api.services.conesearch.conesearch import (
    conesearch_coordinates,
    conesearch_oid,
)
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
    result = conesearch_coordinates(ra, dec, radius, neighbors, mock)

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
    assert [] == conesearch_coordinates(ra, dec, radius, neighbors, mock)


def test_conesearch_oid(mocker):
    # Setup the database mock
    # Result has to be a list of tuples
    # where the first element is the object
    mock = database_mock(
        mocker, [(Object(oid=123, meanra=45.0, meandec=45.0),)]
    )
    implement_context_manager(mocker, mock)

    # Call the service
    result = conesearch_oid(int64(123), 30.0, 10, mock)

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
    result = conesearch_oid(int64(123), 30.0, 10, mock)

    # Assert that the result is as expected
    assert result == []
    mock.execute.assert_called_once()
    call_args = mock.execute.call_args[0]
    assert call_args[1] == {"radius": 30.0}
    assert "123" == str(call_args[0].compile().params["oid_1"])
