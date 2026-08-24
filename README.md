# Production App

MVP untuk mempelajari pembangunan aplikasi production monitoring secara bertahap, dimulai dari typed CSV ingestion hingga API, Database, dan Interface Web.

## Status

Tahap saat ini: D02 - typed ingestion foundation.

Fitur tersedia:

- typed environment configuration;
- validasi header dan struktur baris CSV;
- domain exception untuk input yang invalid;
- CLI untuk menjalankan CSV summary;
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

## Configuration

```bash
cp .env.example .env
```

muat konfigurasi ke terminal:

```bash
set -a
source .env
set +a
```
variabel yang tersedia:

- `APP_ENV`: `development`, `test`, `production`.
- `APP_DATA_DIR`: direktori penyimpanan file CSV.

File `.env` tidak boleh masuk git. `.env.example` hanya berisi contoh aman.
## Local Run

```bash
production-summary readings.csv
```

expected output:

```text
columns: asset_id,value
rows: 2
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
├── data/
│   └── readings.csv
├── docs/
│   └── dev-log.md
├── src/
│   └── production_app/
│       ├── services/
│       │   ├── __init__.py
│       │   └── csv_summary.py
│       ├── __init__.py
│       ├── cli.py
│       ├── config.py
│       └── exceptions.py
├── tests/
│   ├── test_cli.py
│   ├── test_config.py
│   └── test_csv_summary.py
├── .env.example
├── pyproject.toml
└── README.md
```

## CSV contract

CSV valid harus:

- memiliki header;
- kolom tidak boleh kosong;
- kolom tidak boleh duplicate;
- row tidak kekurangan ataupun kelebihan value (sesuai jumlah header).
