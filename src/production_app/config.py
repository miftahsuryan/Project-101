import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from production_app.exceptions import ConfigError

type Environment = Literal["development", "test", "production"]


@dataclass(frozen=True, slots=True)
class AppConfig:
    environment: Environment
    data_dir: Path


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


def load_config() -> AppConfig:
    "Load application configuration from environment variables"
    return AppConfig(
        environment=_parse_environment(os.getenv("APP_ENV", "development")),
        data_dir=Path(os.getenv("APP_DATA_DIR", "data")),
    )
