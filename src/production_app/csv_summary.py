import csv
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class CsvSummary:
    columns: tuple[str, ...]
    row_count: int


def summarize_csv(csv_file: Path) -> CsvSummary:
    "Summarize a CSV file by returning its columns and row count."
    with csv_file.open(mode="r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        columns = tuple(reader.fieldnames or ())
        row_count = sum(1 for _ in reader)

    return CsvSummary(columns=columns, row_count=row_count)
