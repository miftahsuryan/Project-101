from pathlib import Path

import pytest

from production_app.exceptions import CsvIngestionError
from production_app.services.csv_summary import summarize_csv


def test_summarize_csv_returns_columns_and_row_count(tmp_path: Path) -> None:
    csv_file = tmp_path / "readings.csv"
    csv_file.write_text(
        "asset_id,value\nA-01,10\nA-02,20\n",
        encoding="utf-8",
    )

    result = summarize_csv(csv_file)

    assert result.columns == ("asset_id", "value")
    assert result.row_count == 2


def test_summarize_csv_rejects_empty_file(tmp_path: Path) -> None:
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("", encoding="utf-8")

    with pytest.raises(CsvIngestionError, match="header"):
        summarize_csv(csv_file)


@pytest.mark.parametrize(
    ("csv_content", "expected_message"),
    [
        ("asset_id,\nA-01,10\n", "blank"),
        ("asset_id,asset_id\nA-01,A-02\n", "duplicate"),
    ],
)
def test_summarize_csv_rejects_invalid_header(
    tmp_path: Path, csv_content: str, expected_message: str
) -> None:

    csv_file = tmp_path / "invalid-header.csv"
    csv_file.write_text(csv_content, encoding="utf-8")

    with pytest.raises(CsvIngestionError, match=expected_message):
        summarize_csv(csv_file)


@pytest.mark.parametrize(
    ("csv_content", "expected_message"),
    [
        ("asset_id,value\nA-01\n", "missing value"),
        ("asset_id,value\nA01,10,unexpected\n", "extra value"),
    ],
)
def test_summarize_csv_rejects_malformed_rows(
    tmp_path: Path, csv_content: str, expected_message: str
) -> None:

    csv_file = tmp_path / "invalid-row.csv"
    csv_file.write_text(csv_content, encoding="utf-8")

    with pytest.raises(CsvIngestionError, match=expected_message):
        summarize_csv(csv_file)


def test_summarize_csv_reports_missing_file(tmp_path: Path) -> None:
    missing_file = tmp_path / "missing.csv"

    with pytest.raises(CsvIngestionError, match="not found"):
        summarize_csv(missing_file)
