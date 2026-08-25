# Production App

MVP untuk mempelajari pembangunan aplikasi production monitoring secara bertahap, dimulai dari typed CSV ingestion hingga API, Database, dan Interface Web.

## Status

Tahap saat ini: D04 - production API contract.

Fitur tersedia:

- typed environment configuration;
- validasi header dan struktur baris CSV;
- domain exception untuk input yang invalid;
- CLI untuk menjalankan CSV summary;
- automated test dan static quality checks.
- Versioned FastAPI endpoint;
- typed health response;
- OpenAPI and swagger UI;
- prediction request dan response schema;
- consistent API error envelope;
- validation error `422`;
- prediction domain error `409`;
- OpenAPI success dan error contracts.


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

## HTTP API

Jal;ankan development server:

``` bash
APP_ENV=development APP_DATA_DIR=./data\
python3 -m uvicorn production_app.api.app:create_app\
--factory\
--reload\
--host 127.0.0.1\
--port 8000\
```

endpoint yang tersedia:
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Memeriksa status aplikasi |
| `GET` | `/openapi.json` | OpenAPI contract |
| `GET` | `/docs` | Swagger UI |

health response:

```json
{
    "status": "ok",
    "environtment": "development"
}
```
## Prediction API

Endpoint:

```http
POST /api/v1/predictions
```

Valid request:

```json
{
  "asset_id": "A-01",
  "readings": [10.0, 12.0]
}
```

Success response — `200 OK`:

```json
{
  "asset_id": "A-01",
  "predicted_value": 0.0,
  "model_version": "fake-v1"
}
```

Validation error — `422 Unprocessable Content`:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Request validation failed.",
    "details": [
      {
        "field": "asset_id",
        "message": "Validation message"
      }
    ]
  }
}
```

Domain error — `409 Conflict`:

```json
{
  "error": {
    "code": "prediction_unavailable",
    "message": "Prediction is unavailable for asset 'A-404'.",
    "details": []
  }
}
```

## Quality checks

Jalankan seluruh pemeriksaan:

```bash
python3 -m pytest
python3 -m ruff check --no-cache src tests
python3 -m ruff format --check --no-cache src tests
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
│       ├──api/
│       │   ├──routes/
│       │   │    └── health.py
│       │   ├── app.py
│       │   └── schemas.py
│       ├── cli.py
│       ├── config.py
│       └── exceptions.py
├── tests/
│   ├──api/
│   │    ├──test_health.py
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
