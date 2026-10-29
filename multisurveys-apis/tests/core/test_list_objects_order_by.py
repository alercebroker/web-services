"""order_by takes a column of the object or probability tables, or oid_list; anything else answers 400."""

import pytest

from app_client import client_for
from object_api.services.validations import ORDER_BY_COLUMNS


@pytest.fixture
def client(db):
    return client_for("object_api", db, raise_server_exceptions=False)


@pytest.mark.parametrize("path", ["/list_objects", "/htmx/list_objects", "/htmx/side_objects"])
@pytest.mark.parametrize("order_by", ["metadata", "registry", "foo", "Probability"])
def test_unknown_order_by_is_400(client, path, order_by):
    response = client.get(path, params={"survey": "ztf", "order_by": order_by})

    assert response.status_code == 400
    assert response.json()["detail"].startswith("order_by must be oid_list or one of: ")


@pytest.mark.parametrize("order_by", [*ORDER_BY_COLUMNS, "oid_list"])
def test_every_allowed_order_by_answers(client, order_by):
    response = client.get("/list_objects", params={"survey": "ztf", "order_by": order_by})

    assert response.status_code == 200


def test_unknown_order_by_with_an_oid_list_is_400(client):
    response = client.get(
        "/list_objects",
        params={"survey": "ztf", "oid": ["ZTF18abbrrty", "ZTF18ablrncy"], "order_by": "foo", "page_size": 1},
    )

    assert response.status_code == 400
