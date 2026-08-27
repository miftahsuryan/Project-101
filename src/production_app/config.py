import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from production_app.exceptions import ConfigError

type Environment = Literal["development", "test", "production"]

DEFAULT_CORS_ORIGINS = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
)


@dataclass(frozen=True, slots=True)
class AppConfig:
    environment: Environment
    data_dir: Path
    database_url: str | None
    cors_origins: tuple[str, ...] = DEFAULT_CORS_ORIGINS


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


def _parse_cors_origins(
    value: str | None,
) -> tuple[str, ...]:
    if value is None:
        return DEFAULT_CORS_ORIGINS

    origins = tuple(origin.strip() for origin in value.split(",") if origin.strip())

    if not origins:
        raise ConfigError("APP_CORS_ORIGINS must contain at least one origin.")

    return origins


def load_config() -> AppConfig:
    return AppConfig(
        environment=_parse_environment(os.getenv("APP_ENV", "development")),
        data_dir=Path(os.getenv("APP_DATA_DIR", "data")),
        database_url=_parse_database_url(os.getenv("APP_DATABASE_URL")),
        cors_origins=_parse_cors_origins(os.getenv("APP_CORS_ORIGINS")),
    )
