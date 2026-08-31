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


def test_get_summary_executes_queries() -> None:
    session = Mock(spec=Session)
    aggregate_result = Mock()
    aggregate_result.one.return_value = (2, 15.0)
    session.execute.return_value = aggregate_result
    session.scalar.return_value = 20.0

    repository = PostgresReadingRepository(session)

    summary = repository.get_summary()

    assert summary.total == 2
    assert summary.average == 15.0
    assert summary.latest == 20.0
