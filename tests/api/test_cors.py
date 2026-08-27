import pytest
from fastapi.testclient import TestClient

from production_app.api.app import create_app


def test_configured_frontend_can_preflight_asset_request(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    allowed_origin = "https://monitoring.example.com"

    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_CORS_ORIGINS", allowed_origin)

    with TestClient(create_app()) as client:
        response = client.options(
            "/api/v1/assets",
            headers={
                "Origin": allowed_origin,
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == allowed_origin
    assert "POST" in response.headers["access-control-allow-methods"]
