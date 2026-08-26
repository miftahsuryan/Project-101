# Production App

MVP untuk mempelajari pembangunan aplikasi production monitoring secara bertahap, dimulai dari typed CSV ingestion hingga API, Database, dan Interface Web.

## Status

Tahap saat ini: D05 - production service boundary.

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
- immutable Asset domain entity;
- in-memory Asset CRUD service;
- typed Asset API contracts;
- duplicate asset-code protection;
- consistent `404`, `409`, dan `422` error responses;
- Asset CRUD OpenAPI documentation;
- relational design awal pada ERD v0.


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

Endpoint yang tersedia:

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/api/v1/health` | Memeriksa status aplikasi |
| `POST` | `/api/v1/assets` | Membuat asset |
| `GET` | `/api/v1/assets` | Mengambil seluruh asset |
| `GET` | `/api/v1/assets/{asset_id}` | Mengambil satu asset |
| `PUT` | `/api/v1/assets/{asset_id}` | Mengganti data asset |
| `DELETE` | `/api/v1/assets/{asset_id}` | Menghapus asset |
| `POST` | `/api/v1/predictions` | Membuat fake prediction |
| `GET` | `/openapi.json` | Mengambil OpenAPI contract |
| `GET` | `/docs` | Membuka Swagger UI |

health response:

```json
{
    "status": "ok",
    "environtment": "development"
}
```

## Asset API

Asset API menggunakan UUID sebagai identifier internal dan `asset_code`
sebagai identifier bisnis yang unik.

Data saat ini disimpan dalam memory. Seluruh asset akan hilang ketika aplikasi
dihentikan atau dimulai ulang.

Create asset:

```http
POST /api/v1/assets
Content-Type: application/json
```

```json
{
  "asset_code": "PUMP-01",
  "name": "Main Pump"
}
```

Success response — `201 Created`:

```json
{
  "id": "3e29d87a-03b6-43ee-a45a-3eca3d26ca91",
  "asset_code": "PUMP-01",
  "name": "Main Pump"
}
```

List assets:

```http
GET /api/v1/assets
```

Update asset:

```http
PUT /api/v1/assets/{asset_id}
Content-Type: application/json
```

Delete asset:

```http
DELETE /api/v1/assets/{asset_id}
```

Successful delete menghasilkan `204 No Content` tanpa response body.

Jika `asset_code` sudah digunakan, API menghasilkan `409 Conflict`:

```json
{
  "error": {
    "code": "asset_code_conflict",
    "message": "Asset code 'PUMP-01' is already in use.",
    "details": []
  }
}
```

Jika UUID valid tetapi asset tidak ditemukan, API menghasilkan `404 Not Found`.
UUID atau request body yang tidak valid menghasilkan `422 Unprocessable Content`.

Rancangan database berikutnya didokumentasikan pada
[`docs/erd-v0.md`](docs/erd-v0.md).


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
│   ├── dev-log.md
│   └── erd-v0.md
├── src/
│   └── production_app/
│       ├── api/
│       │   ├── routes/
│       │   │   ├── assets.py
│       │   │   ├── health.py
│       │   │   └── predictions.py
│       │   ├── app.py
│       │   ├── error_handlers.py
│       │   └── schemas.py
│       ├── domain/
│       │   └── entities.py
│       ├── services/
│       │   ├── assets.py
│       │   ├── csv_summary.py
│       │   └── predictions.py
│       ├── cli.py
│       ├── config.py
│       └── exceptions.py
├── tests/
│   ├── api/
│   │   ├── test_assets_api.py
│   │   ├── test_health.py
│   │   └── test_predictions.py
│   ├── services/
│   │   └── test_assets.py
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
