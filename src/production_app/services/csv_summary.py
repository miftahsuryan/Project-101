import csv
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from production_app.exceptions import CsvIngestionError


@dataclass(frozen=True, slots=True)
class CsvSummary:
    columns: tuple[str, ...]
    row_count: int


def _validate_headers(fieldnames: list[str]) -> tuple[str, ...]:
    """Validate the header of a CSV file."""
    normalized_headers = tuple(name.strip() for name in fieldnames)

    if any(not name for name in normalized_headers):
        raise CsvIngestionError("CSV header contains blank column name.")

    if len(normalized_headers) != len(set(normalized_headers)):
        raise CsvIngestionError("CSV header contains a duplicate column name")

    return normalized_headers


def _validate_row(
    row: Mapping[str | None, object],
    row_number: int,
) -> None:
    if None in row:
        raise CsvIngestionError(f"CSV row {row_number} contains an extra value")

    if any(value is None for value in row.values()):
        raise CsvIngestionError(f"CSV row {row_number}, contains a missing value")


def summarize_csv(csv_file: Path) -> CsvSummary:
    "Summarize a CSV file by returning its columns and row count."
    try:
        file = csv_file.open(
            mode="r",
            encoding="utf-8",
            newline="",
        )
    except FileNotFoundError as error:
        raise CsvIngestionError(f"CSV file not found: {csv_file}") from error

    with file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise CsvIngestionError("CSV file must have a header row")

        columns = _validate_headers(list(reader.fieldnames))
        row_count = 0

        for row in reader:
            _validate_row(row, reader.line_num)
            row_count += 1

    return CsvSummary(columns=columns, row_count=row_count)
