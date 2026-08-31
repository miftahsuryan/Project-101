from unittest.mock import Mock

from production_app.repositories.readings_repo import ReadingSummary
from production_app.services.overview import OverviewService


def test_get_overview_combines_asset_and_reading_summaries() -> None:
    asset_repository = Mock()
    asset_repository.count.return_value = 2

    reading_repository = Mock()
    reading_repository.get_summary.return_value = ReadingSummary(
        total=4,
        average=15.0,
        latest=20.0,
    )

    overview = OverviewService(
        asset_repository=asset_repository,
        reading_repository=reading_repository,
    ).get_overview()

    assert overview.total_assets == 2
    assert overview.total_readings == 4
    assert overview.average_reading == 15.0
    assert overview.latest_reading == 20.0
