import pytest
from fastapi.testclient import TestClient

from production_app.api.app import create_app


def test_list_readings_returns_paginated_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    with TestClient(create_app()) as client:
        response = client.get(
            "/api/v1/readings?limit=10&offset=0"
        )

    assert response.status_code == 200
    assert response.json() == {
        "items": [],
        "limit": 10,
        "offset": 0,
        "total": 0,
    }


@pytest.mark.parametrize(
    "query",
    [
        "limit=0",
        "limit=101",
        "offset=-1",
    ],
)
def test_list_readings_rejects_invalid_pagination(
    monkeypatch: pytest.MonkeyPatch,
    query: str,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    with TestClient(create_app()) as client:
        response = client.get(f"/api/v1/readings?{query}")

    assert response.status_code == 422


def test_list_readings_documents_response_schema(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "test")

    with TestClient(create_app()) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()
    operation = schema["paths"]["/api/v1/readings"]["get"]

    response_schema = operation["responses"]["200"]["content"][
        "application/json"
    ]["schema"]

    assert response_schema == {
        "$ref": "#/components/schemas/ReadingListResponse"
    }