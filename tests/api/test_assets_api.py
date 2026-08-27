from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from production_app.api.app import create_app


def test_create_asset_can_be_listed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    request_body = {
        "asset_code": "PUMP-01",
        "name": "Main Pump",
    }

    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/v1/assets",
            json=request_body,
        )

        assert create_response.status_code == 201

        created = create_response.json()

        list_response = client.get("/api/v1/assets")

    assert UUID(created["id"])
    assert created["asset_code"] == "PUMP-01"
    assert created["name"] == "Main Pump"

    assert list_response.status_code == 200
    assert list_response.json() == [created]


def test_get_asset_returns_created_asset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/v1/assets",
            json={
                "asset_code": "PUMP-01",
                "name": "Main Pump",
            },
        )
        created = create_response.json()

        detail_response = client.get(f"/api/v1/assets/{created['id']}")

    assert detail_response.status_code == 200
    assert detail_response.json() == created


def test_get_asset_returns_not_found_envelope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    missing_id = uuid4()

    with TestClient(create_app()) as client:
        response = client.get(f"/api/v1/assets/{missing_id}")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "asset_not_found",
            "message": f"Asset {str(missing_id)!r} was not found.",
            "details": [],
        }
    }


def test_get_asset_rejects_invalid_uuid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    with TestClient(create_app()) as client:
        response = client.get("/api/v1/assets/not-a-uuid")

    assert response.status_code == 422

    error = response.json()["error"]

    assert error["code"] == "validation_error"
    assert error["message"] == "Request validation failed."

    invalid_fields = {detail["field"] for detail in error["details"]}

    assert invalid_fields == {"path.asset_id"}


def test_update_asset_replaces_data_and_preserves_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/v1/assets",
            json={
                "asset_code": "PUMP-01",
                "name": "Main Pump",
            },
        )
        created = create_response.json()

        update_response = client.put(
            f"/api/v1/assets/{created['id']}",
            json={
                "asset_code": "PUMP-02",
                "name": "Backup Pump",
            },
        )

        detail_response = client.get(f"/api/v1/assets/{created['id']}")

    assert update_response.status_code == 200

    updated = update_response.json()

    assert updated == {
        "id": created["id"],
        "asset_code": "PUMP-02",
        "name": "Backup Pump",
    }

    assert detail_response.status_code == 200
    assert detail_response.json() == updated


def test_update_asset_returns_conflict_for_duplicate_code(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    with TestClient(create_app()) as client:
        first_response = client.post(
            "/api/v1/assets",
            json={
                "asset_code": "PUMP-01",
                "name": "Main Pump",
            },
        )
        first = first_response.json()

        second_response = client.post(
            "/api/v1/assets",
            json={
                "asset_code": "VALVE-01",
                "name": "Intake Valve",
            },
        )
        second = second_response.json()

        conflict_response = client.put(
            f"/api/v1/assets/{second['id']}",
            json={
                "asset_code": first["asset_code"],
                "name": "Duplicate Pump",
            },
        )

        unchanged_response = client.get(f"/api/v1/assets/{second['id']}")

    assert conflict_response.status_code == 409
    assert conflict_response.json() == {
        "error": {
            "code": "asset_code_conflict",
            "message": ("Asset code 'PUMP-01' is already in use."),
            "details": [],
        }
    }

    assert unchanged_response.status_code == 200
    assert unchanged_response.json() == second


def test_create_asset_returns_conflict_for_duplicate_code(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    request_body = {
        "asset_code": "PUMP-01",
        "name": "Main Pump",
    }

    with TestClient(create_app()) as client:
        first_response = client.post(
            "/api/v1/assets",
            json=request_body,
        )

        conflict_response = client.post(
            "/api/v1/assets",
            json={
                "asset_code": "PUMP-01",
                "name": "Duplicate Pump",
            },
        )

        list_response = client.get("/api/v1/assets")

    assert first_response.status_code == 201

    assert conflict_response.status_code == 409
    assert conflict_response.json() == {
        "error": {
            "code": "asset_code_conflict",
            "message": "Asset code 'PUMP-01' is already in use.",
            "details": [],
        }
    }

    assert list_response.status_code == 200
    assert list_response.json() == [first_response.json()]


def test_delete_asset_removes_created_asset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    with TestClient(create_app()) as client:
        create_response = client.post(
            "/api/v1/assets",
            json={
                "asset_code": "PUMP-01",
                "name": "Main Pump",
            },
        )
        created = create_response.json()

        delete_response = client.delete(
            f"/api/v1/assets/{created['id']}",
        )

        detail_response = client.get(
            f"/api/v1/assets/{created['id']}",
        )

    assert create_response.status_code == 201

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    assert detail_response.status_code == 404
    assert detail_response.json()["error"]["code"] == "asset_not_found"


def test_delete_asset_returns_not_found_envelope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    missing_id = uuid4()

    with TestClient(create_app()) as client:
        response = client.delete(
            f"/api/v1/assets/{missing_id}",
        )

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "asset_not_found",
            "message": f"Asset {str(missing_id)!r} was not found.",
            "details": [],
        }
    }


def test_delete_asset_rejects_invalid_uuid(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    with TestClient(create_app()) as client:
        response = client.delete(
            "/api/v1/assets/not-a-uuid",
        )

    assert response.status_code == 422

    error = response.json()["error"]

    assert error["code"] == "validation_error"
    assert error["message"] == "Request validation failed."

    invalid_fields = {detail["field"] for detail in error["details"]}

    assert invalid_fields == {"path.asset_id"}


def test_delete_asset_documents_http_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    with TestClient(create_app()) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200

    openapi_schema = response.json()
    delete_operation = openapi_schema["paths"]["/api/v1/assets/{asset_id}"]["delete"]

    responses = delete_operation["responses"]

    assert set(responses) == {"204", "404", "422"}

    assert "content" not in responses["204"]

    assert responses["404"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/ErrorResponse"
    }

    assert responses["422"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/ErrorResponse"
    }


def test_list_assets_filters_by_asset_code(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    with TestClient(create_app()) as client:
        first_response = client.post(
            "/api/v1/assets",
            json={
                "asset_code": "PUMP-01",
                "name": "Main Pump",
            },
        )

        second_response = client.post(
            "/api/v1/assets",
            json={
                "asset_code": "VALVE-01",
                "name": "Intake Valve",
            },
        )

        list_response = client.get(
            "/api/v1/assets",
            params={"asset_code": "PUMP-01"},
        )

    assert first_response.status_code == 201
    assert second_response.status_code == 201
    assert list_response.status_code == 200
    assert list_response.json() == [first_response.json()]


def test_list_assets_applies_limit_and_offset(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    created_assets: list[dict[str, object]] = []

    with TestClient(create_app()) as client:
        for number in range(1, 4):
            create_response = client.post(
                "/api/v1/assets",
                json={
                    "asset_code": f"PUMP-{number:02}",
                    "name": f"Pump {number}",
                },
            )

            assert create_response.status_code == 201
            created_assets.append(create_response.json())

        list_response = client.get(
            "/api/v1/assets",
            params={
                "limit": 2,
                "offset": 1,
            },
        )

    assert list_response.status_code == 200
    assert list_response.json() == created_assets[1:3]


@pytest.mark.parametrize(
    ("params", "invalid_field"),
    [
        pytest.param(
            {"limit": 0},
            "query.limit",
            id="limit-too-small",
        ),
        pytest.param(
            {"limit": 101},
            "query.limit",
            id="limit-too-large",
        ),
        pytest.param(
            {"offset": -1},
            "query.offset",
            id="offset-negative",
        ),
    ],
)
def test_list_assets_rejects_invalid_pagination(
    monkeypatch: pytest.MonkeyPatch,
    params: dict[str, int],
    invalid_field: str,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    with TestClient(create_app()) as client:
        response = client.get(
            "/api/v1/assets",
            params=params,
        )

    assert response.status_code == 422

    error = response.json()["error"]

    assert error["code"] == "validation_error"
    assert error["message"] == "Request validation failed."

    invalid_fields = {detail["field"] for detail in error["details"]}

    assert invalid_fields == {invalid_field}


def test_list_assets_documents_pagination_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    with TestClient(create_app()) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200

    openapi_schema = response.json()
    list_operation = openapi_schema["paths"]["/api/v1/assets"]["get"]

    parameters = {
        parameter["name"]: parameter for parameter in list_operation["parameters"]
    }

    assert set(parameters) == {
        "asset_code",
        "limit",
        "offset",
    }

    limit_schema = parameters["limit"]["schema"]

    assert limit_schema["minimum"] == 1
    assert limit_schema["maximum"] == 100
    assert limit_schema["default"] == 20

    offset_schema = parameters["offset"]["schema"]

    assert offset_schema["minimum"] == 0
    assert offset_schema["default"] == 0

    validation_schema = list_operation["responses"]["422"]["content"][
        "application/json"
    ]["schema"]

    assert validation_schema == {"$ref": "#/components/schemas/ErrorResponse"}
