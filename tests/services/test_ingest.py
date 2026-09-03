from collections.abc import Sequence
from pathlib import Path

from production_app.domain.entities import Reading
from production_app.repositories.readings_repo import ReadingPage, ReadingSummary
from production_app.services.ingest import IngestService


class FakeReadingRepository:
    def __init__(self) -> None:
        self.readings: list[Reading] = []

    def add_many(self, readings: Sequence[Reading]) -> None:
        self.readings.extend(readings)

    def get_summary(self) -> ReadingSummary:
        total = len(self.readings)
        if total == 0:
            return ReadingSummary(total=0, average=None, latest=None)
        avg = sum(r.value for r in self.readings) / total
        latest = self.readings[-1].value
        return ReadingSummary(total=total, average=avg, latest=latest)

    def list_page(
        self,
        *,
        asset_code: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> ReadingPage:
        items = self.readings
        if asset_code is not None:
            items = [r for r in items if r.asset_code == asset_code]
        page_items = items[offset : offset + limit]
        return ReadingPage(items=page_items, total=len(items))


def test_parse_readings_deduplicates_rows(tmp_path: Path) -> None:
    csv_file = tmp_path / "readings.csv"
    csv_file.write_text(
        "asset_id,value\nA-01,10\nA-01,10\nA-02,20\n",
        encoding="utf-8",
    )

    repository = FakeReadingRepository()
    readings = IngestService(repository).parse_readings(csv_file)

    assert len(readings) == 2
    assert readings[0].asset_code == "A-01"
    assert readings[0].value == 10.0
    assert readings[1].asset_code == "A-02"
    assert readings[1].value == 20.0


def test_ingest_csv_persists_parsed_readings(tmp_path: Path) -> None:
    csv_file = tmp_path / "readings.csv"
    csv_file.write_text(
        "asset_id,value\nA-01,10\nA-02,20\n",
        encoding="utf-8",
    )

    repository = FakeReadingRepository()
    service = IngestService(repository)

    imported_count = service.ingest_csv(csv_file)

    assert imported_count == 2
    assert len(repository.readings) == 2
    assert repository.readings[0].asset_code == "A-01"
    assert repository.readings[1].value == 20.0


def test_parse_readings_is_deterministic(tmp_path: Path) -> None:
    csv_file = tmp_path / "readings.csv"
    csv_file.write_text(
        "asset_id,value\nA-01,10\n",
        encoding="utf-8",
    )

    first = IngestService(
        FakeReadingRepository(),
    ).parse_readings(csv_file)

    second = IngestService(
        FakeReadingRepository(),
    ).parse_readings(csv_file)

    assert first[0].id == second[0].id
