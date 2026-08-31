import pytest
from fastapi.testclient import TestClient

from production_app.api.app import create_app


def test_overview_returns_empty_summary_in_test_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    with TestClient(create_app()) as client:
        response = client.get("/api/v1/overview")

    assert response.status_code == 200
    assert response.json() == {
        "total_assets": 0,
        "total_readings": 0,
        "average_reading": None,
        "latest_reading": None,
    }


def test_overview_is_documented_in_openapi(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    with TestClient(create_app()) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()
    operation = schema["paths"]["/api/v1/overview"]["get"]

    response_schema = operation["responses"]["200"]["content"]["application/json"][
        "schema"
    ]

    assert response_schema == {"$ref": "#/components/schemas/OverviewResponse"}
