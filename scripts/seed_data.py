import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path
from uuid import NAMESPACE_URL, UUID, uuid5

from production_app.config import load_config
from production_app.database.session import (
    create_database_engine,
    create_session_factory,
)
from production_app.domain.entities import Asset, Reading
from production_app.repositories.postgres_assets import PostgresAssetRepository
from production_app.repositories.postgres_readings import (
    PostgresReadingRepository,
)


@dataclass(frozen=True)
class SeedData:
    assets: list[Asset]
    readings: list[Reading]


def generate_asset_id(asset_code: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"production-app:asset:{asset_code}")


def generate_reading_id(asset_code: str, value: float) -> UUID:
    return uuid5(NAMESPACE_URL, f"production-app:reading:{asset_code}:{value}")


def _sort_key(row: dict[str, str]) -> tuple[int, str]:
    raw_udi = row.get("UDI", "").strip()
    udi = int(raw_udi) if raw_udi.isdigit() else 0
    return (udi, row.get("Product ID", ""))


def extract_seed_data(
    source_csv: Path,
    sample_size: int = 20,
) -> SeedData:
    """Extract a balanced, deterministic subset of assets and readings.

    Selects half normal machines and half machines with failure or high wear.
    """
    if not source_csv.exists():
        raise FileNotFoundError(f"Source CSV not found: {source_csv}")

    normal_rows: list[dict[str, str]] = []
    failure_rows: list[dict[str, str]] = []

    with source_csv.open(
        mode="r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row.get("Machine failure") == "1":
                failure_rows.append(row)
            else:
                normal_rows.append(row)

    normal_rows.sort(key=_sort_key)
    failure_rows.sort(key=_sort_key)

    half_sample = max(1, sample_size // 2)
    selected_normal = normal_rows[:half_sample]
    selected_failure = failure_rows[:half_sample]
    combined = selected_normal + selected_failure

    assets: list[Asset] = []
    readings: list[Reading] = []

    for row in combined:
        product_id = row["Product ID"].strip()
        product_type = row.get("Type", "Standard").strip()
        torque = float(row.get("Torque [Nm]", "0.0"))

        asset_code = product_id
        name = f"Milling Machine {product_id} ({product_type}-Type)"
        asset_id = generate_asset_id(asset_code)

        assets.append(Asset(id=asset_id, asset_code=asset_code, name=name))
        readings.append(
            Reading(
                id=generate_reading_id(asset_code, torque),
                asset_code=asset_code,
                value=torque,
            )
        )

    return SeedData(assets=assets, readings=readings)


def write_seed_files(
    seed_data: SeedData,
    assets_path: Path,
    readings_path: Path,
) -> None:
    """Write seed data to CSV fixtures."""
    assets_path.parent.mkdir(parents=True, exist_ok=True)
    readings_path.parent.mkdir(parents=True, exist_ok=True)

    with assets_path.open(mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["asset_code", "name"])
        for asset in seed_data.assets:
            writer.writerow([asset.asset_code, asset.name])

    with readings_path.open(mode="w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["asset_id", "value"])
        for reading in seed_data.readings:
            writer.writerow([reading.asset_code, reading.value])


def seed_to_database(seed_data: SeedData) -> tuple[int, int]:
    """Persist seed assets and readings into PostgreSQL."""
    config = load_config()
    if config.database_url is None:
        raise ValueError("APP_DATABASE_URL is not set in environment or config.")

    engine = create_database_engine(config.database_url)
    session_factory = create_session_factory(engine)

    inserted_assets = 0
    with session_factory() as session:
        asset_repo = PostgresAssetRepository(session)
        for asset in seed_data.assets:
            if asset_repo.get_by_code(asset.asset_code) is None:
                asset_repo.add(asset)
                inserted_assets += 1
        session.commit()

    with session_factory() as session:
        reading_repo = PostgresReadingRepository(session)
        reading_repo.add_many(seed_data.readings)
        session.commit()

    return inserted_assets, len(seed_data.readings)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract and seed deterministic tabular data from ai4i2020.csv."
    )
    parser.add_argument(
        "--input-csv",
        type=Path,
        default=Path("data/ai4i2020.csv"),
        help="Path to source AI4I dataset.",
    )
    parser.add_argument(
        "--output-assets",
        type=Path,
        default=Path("data/seed_assets.csv"),
        help="Path to output assets seed CSV.",
    )
    parser.add_argument(
        "--output-readings",
        type=Path,
        default=Path("data/seed_readings.csv"),
        help="Path to output readings seed CSV.",
    )
    parser.add_argument(
        "--sample-size",
        type=int,
        default=20,
        help="Number of representative assets to extract (half normal, half failure).",
    )
    parser.add_argument(
        "--load-db",
        action="store_true",
        help="Persist seed data directly into PostgreSQL.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        seed_data = extract_seed_data(args.input_csv, args.sample_size)
        write_seed_files(seed_data, args.output_assets, args.output_readings)

        print(
            f"Wrote {len(seed_data.assets)} assets to {args.output_assets} "
            f"and {len(seed_data.readings)} readings to {args.output_readings}."
        )

        if args.load_db:
            new_assets, total_readings = seed_to_database(seed_data)
            print(
                f"Database seeded: {new_assets} new assets, "
                f"{total_readings} readings processed."
            )

    except Exception as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
