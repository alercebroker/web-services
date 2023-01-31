from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient
from fastapi import FastAPI
from pytest_mock.plugin import MockerFixture
from ralidator_core.ralidator_core import Ralidator

from ralidator_fastapi.ralidator_fastapi import RalidatorStarlette

app = FastAPI()
app.add_middleware(
    RalidatorStarlette, config={"SECRET_KEY": "test"}, filters_map={}
)

test_response = {"msg": "Hello World"}


@app.get("/")
async def read_main():
    return test_response


client = TestClient(app)


def test_auth_without_token(mocker: MockerFixture):
    apply_filters = mocker.patch.object(
        RalidatorStarlette, "apply_ralidator_filters"
    )
    apply_filters.return_value = JSONResponse(test_response)
    authenticate_token = mocker.patch.object(Ralidator, "authenticate_token")
    response = client.get("/")
    authenticate_token.assert_called_with(None)
    assert response.status_code == 200


def test_filters(mocker: MockerFixture):
    apply_filters = mocker.patch.object(Ralidator, "apply_filters")
    apply_filters.return_value = test_response
    response = client.get("/")
    assert response.status_code == 200
    apply_filters.assert_called_with(test_response)
    assert response.json() == test_response
