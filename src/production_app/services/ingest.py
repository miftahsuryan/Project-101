import csv
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from production_app.domain.entities import Reading
from production_app.exceptions import CsvIngestionError
from production_app.repositories.readings_repo import ReadingRepository
from production_app.services.csv_summary import summarize_csv


class IngestService:
    def __init__(self, repository: ReadingRepository) -> None:
        self._repository = repository

    def ingest_csv(self, csv_file: Path) -> int:
        readings = self.parse_readings(csv_file)
        self._repository.add_many(readings)
        return len(readings)

    def parse_readings(self, csv_file: Path) -> list[Reading]:
        summary = summarize_csv(csv_file)

        if summary.columns != ("asset_id", "value"):
            raise CsvIngestionError("Reading CSV must contain exactly: asset_id,value")

        readings_by_key: dict[tuple[str, float], Reading] = {}

        with csv_file.open(
            mode="r",
            encoding="utf-8",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            for row in reader:
                asset_code = (row["asset_id"] or "").strip()
                raw_value = (row["value"] or "").strip()

                try:
                    value = float(raw_value)
                except ValueError as error:
                    raise CsvIngestionError(
                        f"Invalid reading value: {raw_value!r}"
                    ) from error

                key = (asset_code, value)

                readings_by_key[key] = Reading(
                    id=uuid5(
                        NAMESPACE_URL,
                        f"production-app:reading:{asset_code}:{value}",
                    ),
                    asset_code=asset_code,
                    value=value,
                )

        return list(readings_by_key.values())
