from dataclasses import dataclass

from production_app.repositories.assets_repo import AssetRepository
from production_app.repositories.readings_repo import (
    ReadingRepository,
    ReadingSummary,
)


@dataclass(frozen=True)
class Overview:
    total_assets: int
    total_readings: int
    average_reading: float | None
    latest_reading: float | None


class OverviewService:
    def __init__(
        self,
        asset_repository: AssetRepository,
        reading_repository: ReadingRepository,
    ) -> None:
        self._asset_repository = asset_repository
        self._reading_repository = reading_repository

    def get_overview(self) -> Overview:
        reading_summary: ReadingSummary = self._reading_repository.get_summary()

        return Overview(
            total_assets=self._asset_repository.count(),
            total_readings=reading_summary.total,
            average_reading=reading_summary.average,
            latest_reading=reading_summary.latest,
        )
