import pytest
from fastapi.testclient import TestClient

from production_app.api.app import create_app


def test_create_prediction_returns_validation_error_envelope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    invalid_request = {
        "asset_id": "",
        "readings": [],
    }

    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/predictions",
            json=invalid_request,
        )

    assert response.status_code == 422

    error = response.json()["error"]
    assert error["code"] == "validation_error"
    assert error["message"] == "Request validation failed."

    invalid_fields = {detail["field"] for detail in error["details"]}

    assert invalid_fields == {
        "asset_id",
        "readings",
    }


def test_create_prediction_returns_fake_prediction(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    valid_request = {"asset_id": "A-01", "readings": [10.0, 12.0]}

    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/predictions",
            json=valid_request,
        )

    assert response.status_code == 200
    assert response.json() == {
        "asset_id": "A-01",
        "predicted_value": 0.0,
        "model_version": "fake-v1",
    }


def test_prediction_documents_validation_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    with TestClient(create_app()) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200

    openapi_schema = response.json()
    prediction_operation = openapi_schema["paths"]["/api/v1/predictions"]["post"]

    validation_schema = prediction_operation["responses"]["422"]["content"][
        "application/json"
    ]["schema"]

    assert validation_schema == {"$ref": "#/components/schemas/ErrorResponse"}


def test_create_prediction_returns_domain_error_envelope(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    valid_but_unavailable_request = {
        "asset_id": "A-404",
        "readings": [10.0, 12.0],
    }

    with TestClient(create_app()) as client:
        response = client.post(
            "/api/v1/predictions",
            json=valid_but_unavailable_request,
        )

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "prediction_unavailable",
            "message": ("Prediction is unavailable for asset 'A-404'."),
            "details": [],
        }
    }


def test_prediction_documents_domain_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    with TestClient(create_app()) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200

    openapi_schema = response.json()
    prediction_operation = openapi_schema["paths"]["/api/v1/predictions"]["post"]

    domain_error_schema = prediction_operation["responses"]["409"]["content"][
        "application/json"
    ]["schema"]

    assert domain_error_schema == {"$ref": "#/components/schemas/ErrorResponse"}
