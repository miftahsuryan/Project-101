import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from production_app.exceptions import ConfigError

type Environment = Literal["development", "test", "production"]


@dataclass(frozen=True, slots=True)
class AppConfig:
    environment: Environment
    data_dir: Path
    database_url: str | None


def _parse_environment(value: str) -> Environment:
    if value == "development":
        return "development"

    if value == "test":
        return "test"

    if value == "production":
        return "production"

    raise ConfigError(
        f"APP_ENV must be development, test, or production; received {value!r}."
    )


def _parse_database_url(
    value: str | None,
) -> str | None:
    if value is None:
        return None

    try:
        parsed = urlsplit(value)
        _ = parsed.port
    except ValueError as error:
        raise ConfigError("APP_DATABASE_URL contains an invalid port.") from error

    database_name = parsed.path.lstrip("/")

    if (
        value.strip() != value
        or parsed.scheme != "postgresql"
        or parsed.hostname is None
        or not database_name
    ):
        raise ConfigError(
            "APP_DATABASE_URL must use postgresql:// "
            "and include a host and database name."
        )

    return value


def load_config() -> AppConfig:
    """Load application configuration from environment variables."""
    return AppConfig(
        environment=_parse_environment(os.getenv("APP_ENV", "development")),
        data_dir=Path(os.getenv("APP_DATA_DIR", "data")),
        database_url=_parse_database_url(os.getenv("APP_DATABASE_URL")),
    )
