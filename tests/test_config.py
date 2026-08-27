from pathlib import Path

import pytest

from production_app.config import AppConfig, load_config
from production_app.exceptions import ConfigError


def test_load_config_uses_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("APP_DATA_DIR", raising=False)
    monkeypatch.delenv("APP_DATABASE_URL", raising=False)
    monkeypatch.delenv("APP_CORS_ORIGINS", raising=False)
    config = load_config()

    assert config == AppConfig(
        environment="development",
        data_dir=Path("data"),
        database_url=None,
    )


def test_load_config_reads_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_url = (
        "postgresql://production_app:production_app@localhost:5432/production_app"
    )

    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv(
        "APP_DATA_DIR",
        "/tmp/production-app-data",
    )
    monkeypatch.setenv(
        "APP_DATABASE_URL",
        database_url,
    )
    config = load_config()

    assert config == AppConfig(
        environment="test",
        data_dir=Path("/tmp/production-app-data"),
        database_url=database_url,
    )


def test_load_config_rejects_invalid_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "prodution")

    with pytest.raises(ConfigError, match="APP_ENV"):
        load_config()


@pytest.mark.parametrize(
    "database_url",
    [
        pytest.param(
            "",
            id="empty",
        ),
        pytest.param(
            "not-a-url",
            id="invalid-format",
        ),
        pytest.param(
            "mysql://user:password@localhost/app",
            id="unsupported-scheme",
        ),
        pytest.param(
            "postgresql://",
            id="missing-host-and-database",
        ),
    ],
)
def test_load_config_rejects_invalid_database_url(
    monkeypatch: pytest.MonkeyPatch,
    database_url: str,
) -> None:
    monkeypatch.setenv(
        "APP_DATABASE_URL",
        database_url,
    )

    with pytest.raises(
        ConfigError,
        match="APP_DATABASE_URL",
    ):
        load_config()


def test_load_config_reads_cors_origins(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "APP_CORS_ORIGINS",
        ("http://localhost:3000,https://monitoring.example.com"),
    )

    config = load_config()

    assert config.cors_origins == (
        "http://localhost:3000",
        "https://monitoring.example.com",
    )
