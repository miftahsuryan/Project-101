import pytest
from fastapi.testclient import TestClient

from production_app.api.app import create_app


def test_health_returns_application_status(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    monkeypatch.setenv("APP_ENV", "test")

    app = create_app()

    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "environment": "test",
    }


def test_health_is_only_available_under_versioned_api(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    with TestClient(create_app()) as client:
        response = client.get("/health")

        assert response.status_code == 404


def test_health_is_documented_in_openapi(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    with TestClient(create_app()) as client:
        response = client.get("/openapi.json")

        assert response.status_code == 200

        openapi_schema = response.json()
        health_operation = openapi_schema["paths"]["/api/v1/health"]["get"]
        response_schema = health_operation["responses"]["200"]["content"][
            "application/json"
        ]["schema"]
        assert response_schema == {"$ref": "#/components/schemas/HealthResponse"}
