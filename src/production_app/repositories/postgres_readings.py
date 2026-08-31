from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from production_app.database.models import ReadingModel
from production_app.domain.entities import Reading
from production_app.repositories.readings_repo import (
    ReadingRepository,
    ReadingSummary,
)


class PostgresReadingRepository(ReadingRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def add_many(self, readings: Sequence[Reading]) -> None:
        if not readings:
            return

        values = [
            {
                "id": reading.id,
                "asset_code": reading.asset_code,
                "value": reading.value,
            }
            for reading in readings
        ]

        statement = insert(ReadingModel).values(values)
        statement = statement.on_conflict_do_nothing(
            index_elements=[ReadingModel.id],
        )

        self._session.execute(statement)

    def get_summary(self) -> ReadingSummary:
        aggregate_statement = select(
            func.count(ReadingModel.id),
            func.avg(ReadingModel.value),
        )

        total, average = self._session.execute(aggregate_statement).one()

        latest_statement = (
            select(ReadingModel.value)
            .order_by(
                ReadingModel.created_at.desc(),
                ReadingModel.id.desc(),
            )
            .limit(1)
        )

        latest = self._session.scalar(latest_statement)

        return ReadingSummary(
            total=int(total or 0),
            average=None if average is None else float(average),
            latest=None if latest is None else float(latest),
        )
