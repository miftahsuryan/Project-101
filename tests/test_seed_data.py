from pathlib import Path

from scripts.seed_data import extract_seed_data, write_seed_files


def test_extract_seed_data_is_deterministic(tmp_path: Path) -> None:
    source_csv = Path("data/ai4i2020.csv")
    first = extract_seed_data(source_csv, sample_size=10)
    second = extract_seed_data(source_csv, sample_size=10)

    assert len(first.assets) == 10
    assert len(first.readings) == 10
    assert first.assets == second.assets
    assert first.readings == second.readings


def test_write_seed_files_creates_valid_csvs(tmp_path: Path) -> None:
    source_csv = Path("data/ai4i2020.csv")
    seed_data = extract_seed_data(source_csv, sample_size=6)

    assets_file = tmp_path / "assets.csv"
    readings_file = tmp_path / "readings.csv"

    write_seed_files(seed_data, assets_file, readings_file)

    assert assets_file.exists()
    assert readings_file.exists()

    assets_content = assets_file.read_text(encoding="utf-8").splitlines()
    assert assets_content[0] == "asset_code,name"
    assert len(assets_content) == 7  # 1 header + 6 rows

    readings_content = readings_file.read_text(encoding="utf-8").splitlines()
    assert readings_content[0] == "asset_id,value"
    assert len(readings_content) == 7  # 1 header + 6 rows
