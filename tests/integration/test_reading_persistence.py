from uuid import uuid4

import pytest
from sqlalchemy import func, select

from production_app.config import load_config
from production_app.database.models import ReadingModel
from production_app.database.session import (
    create_database_engine,
    create_session_factory,
)
from production_app.domain.entities import Reading
from production_app.repositories.postgres_readings import (
    PostgresReadingRepository,
)


@pytest.mark.integration
def test_add_many_is_idempotent() -> None:
    config = load_config()

    if config.database_url is None:
        pytest.skip("APP_DATABASE_URL is not configured.")

    engine = create_database_engine(config.database_url)
    session_factory = create_session_factory(engine)

    reading = Reading(
        id=uuid4(),
        asset_code="A-01",
        value=10.0,
    )

    try:
        with session_factory() as session:
            repository = PostgresReadingRepository(session)

            repository.add_many([reading])
            session.commit()

            repository.add_many([reading])
            session.commit()

            count = session.scalar(
                select(func.count())
                .select_from(ReadingModel)
                .where(ReadingModel.id == reading.id)
            )

            assert count == 1
    finally:
        with session_factory() as session:
            model = session.get(ReadingModel, reading.id)

            if model is not None:
                session.delete(model)
                session.commit()
