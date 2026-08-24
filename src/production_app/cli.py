import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from production_app.config import load_config
from production_app.exceptions import ProductionAppError
from production_app.services.csv_summary import summarize_csv


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
