# Production App

MVP untuk mempelajari pembangunan aplikasi production monitoring secara bertahap, dimulai dari typed CSV ingestion hingga API, Database, dan Interface Web.

## Status

Tahap saat ini: D01 - engineering baseline

Fitur tersedia:

- membaca header CSV;
- menghitung jumlah baris dan CSV;
- hasil bertipe melalui `CsvSummary`;
- automated test dan static quality checks.

## Requirements

- Python 3.12 atau yang lebih baru
- Git

## Setup

Buat dan aktifkan virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install package dan development tools:

```bash
python3 -m pip install -e ".[dev]"
```

## Quality checks

Jalankan seluruh pemeriksaan:

```bash
python3 -m pytest
python3 -m ruff check src tests
python3 -m ruff format --check src tests
python3 -m mypy
```
## Project structure

```text
.
├── src/
│   └── production_app/
│       ├── __init__.py
│       └── csv_summary.py
├── tests/
│   └── test_csv_summary.py
├── pyproject.toml
└── README.md
```

## Current CSV contract

Input:

```csv
asset_id, value
A-01,10
A-02,20
```

Result"

```python
CsvSummary(
    columns=("asset_id", "value"),
    row_count=2,
)
```

Validasi CSV kosong atau rusak akan ditambahkan pada tahap D02