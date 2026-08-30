from unittest.mock import Mock
from uuid import uuid4

from sqlalchemy.orm import Session

from production_app.domain.entities import Reading
from production_app.repositories.postgres_readings import (
    PostgresReadingRepository,
)


def test_add_many_executes_bulk_insert() -> None:
    readings = [
        Reading(
            id=uuid4(),
            asset_code="A-01",
            value=10.0,
        ),
        Reading(
            id=uuid4(),
            asset_code="A-02",
            value=20.0,
        ),
    ]

    session = Mock(spec=Session)
    repository = PostgresReadingRepository(session)

    repository.add_many(readings)

    session.execute.assert_called_once()
