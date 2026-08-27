import pytest

from production_app.config import load_config
from production_app.database.connection import ping_database


@pytest.mark.integration
def test_database_ping_executes_select_one() -> None:
    config = load_config()

    if config.database_url is None:
        pytest.skip("APP_DATABASE_URL is not configured.")

    assert ping_database(config.database_url) is True
