from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from production_app.database.models import ReadingModel
from production_app.domain.entities import Reading


class PostgresReadingRepository:
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

    def list_readings(
        self,
        *,
        asset_code: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Reading]:
        statement = select(ReadingModel).order_by(
            ReadingModel.created_at,
            ReadingModel.id,
        )

        if asset_code is not None:
            statement = statement.where(ReadingModel.asset_code == asset_code)

        statement = statement.limit(limit).offset(offset)

        models = self._session.scalars(statement).all()

        return [
            Reading(
                id=model.id,
                asset_code=model.asset_code,
                value=model.value,
            )
            for model in models
        ]
