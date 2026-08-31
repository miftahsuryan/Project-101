from production_app.repositories.readings_repo import (
    ReadingPage,
    ReadingRepository,
)


class ReadingService:
    def __init__(self, repository: ReadingRepository) -> None:
        self._repository = repository

    def list_readings(
        self,
        *,
        asset_code: str | None,
        limit: int,
        offset: int,
    ) -> ReadingPage:
        return self._repository.list_page(
            asset_code=asset_code,
            limit=limit,
            offset=offset,
        )