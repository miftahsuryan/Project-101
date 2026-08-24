from pathlib import Path

import pytest

from production_app.config import AppConfig, load_config
from production_app.exceptions import ConfigError


def test_load_config_uses_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.delenv("APP_DATA_DIR", raising=False)

    config = load_config()

    assert config == AppConfig(
        environment="development",
        data_dir=Path("data"),
    )


def test_load_config_reads_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_DATA_DIR", "/tmp/production-app-data")

    config = load_config()

    assert config == AppConfig(
        environment="test", data_dir=Path("/tmp/production-app-data")
    )


def test_load_config_rejects_invalid_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "prodution")

    with pytest.raises(ConfigError, match="APP_ENV"):
        load_config()
