from pathlib import Path

import pytest

from production_app.cli import main


def test_main_summarizes_csv(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    csv_file = tmp_path / "readings.csv"
    csv_file.write_text(
        "asset_id,value\nA-01,10\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_DATA_DIR", str(tmp_path))

    exit_code = main(["readings.csv"])

    captured = capsys.readouterr()

    assert exit_code == 0
    assert captured.out == ("columns: asset_id,value\nrows: 1\n")
    assert captured.err == ""


def test_main_reports_csv_ingestion_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("", encoding="utf-8")

    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("APP_DATA_DIR", str(tmp_path))

    exit_code = main(["empty.csv"])

    captured = capsys.readouterr()

    assert exit_code == 1
    assert captured.out == ""
    assert captured.err == "error: CSV file must have a header row\n"
