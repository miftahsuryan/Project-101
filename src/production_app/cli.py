import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from production_app.config import load_config
from production_app.database.session import (
    create_database_engine,
    create_session_factory,
)
from production_app.exceptions import ProductionAppError
from production_app.repositories.postgres_readings import (
    PostgresReadingRepository,
)
from production_app.services.csv_summary import summarize_csv
from production_app.services.ingest import IngestService


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize a CSV file.",
    )
    parser.add_argument(
        "csv_file",
        type=Path,
        help="CSV filename relative to APP_DATA_DIR.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CSV summary command."""
    parser = _build_parser()
    arguments = parser.parse_args(argv)

    try:
        config = load_config()
        csv_file = config.data_dir / arguments.csv_file
        summary = summarize_csv(csv_file)
    except ProductionAppError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print(f"columns: {','.join(summary.columns)}")
    print(f"rows: {summary.row_count}")

    return 0


def ingest_main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Import readings CSV into PostgreSQL.",
    )
    parser.add_argument(
        "csv_file",
        type=Path,
        help="CSV filename relative to APP_DATA_DIR.",
    )

    arguments = parser.parse_args(argv)

    try:
        config = load_config()

        if config.database_url is None:
            raise ProductionAppError(
                "APP_DATABASE_URL is required for production ingestion."
            )

        csv_file = config.data_dir / arguments.csv_file
        engine = create_database_engine(config.database_url)
        session_factory = create_session_factory(engine)

        with session_factory() as session:
            try:
                repository = PostgresReadingRepository(session)
                service = IngestService(repository)
                imported_count = service.ingest_csv(csv_file)
                session.commit()
            except Exception:
                session.rollback()
                raise

    except ProductionAppError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    print(f"imported: {imported_count}")
    return 0
