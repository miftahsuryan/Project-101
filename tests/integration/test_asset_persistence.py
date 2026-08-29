from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from production_app.api.app import create_app
from production_app.config import load_config


@pytest.mark.integration
def test_asset_survives_app_recreation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    config = load_config()

    if config.database_url is None:
        pytest.skip("APP_DATABASE_URL is not configured.")

    monkeypatch.setenv("APP_ENV", "development")

    asset_code = f"TEST-{uuid4().hex[:12].upper()}"

    with TestClient(create_app()) as first_client:
        create_response = first_client.post(
            "/api/v1/assets",
            json={
                "asset_code": asset_code,
                "name": "Persistence Test Asset",
            },
        )

    assert create_response.status_code == 201
    created = create_response.json()

    try:
        with TestClient(create_app()) as second_client:
            get_response = second_client.get(f"/api/v1/assets/{created['id']}")

        assert get_response.status_code == 200
        assert get_response.json() == created
    finally:
        with TestClient(create_app()) as cleanup_client:
            cleanup_client.delete(f"/api/v1/assets/{created['id']}")
