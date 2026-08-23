from pathlib import Path

from production_app.csv_summary import summarize_csv


def test_summarize_csv_returns_columns_and_row_count(tmp_path: Path) -> None:
    csv_file = tmp_path / "readings.csv"
    csv_file.write_text(
        "asset_id,value\nA-01,10\nA-02,20\n",
        encoding="utf-8",
    )

    result = summarize_csv(csv_file)

    assert result.columns == ("asset_id", "value")
    assert result.row_count == 2
