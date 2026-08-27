# Production App

MVP untuk mempelajari pembangunan aplikasi production monitoring secara bertahap, dimulai dari typed CSV ingestion hingga API, Database, dan Interface Web.

## Status

Tahap saat ini: D07 - Milestone v0.1 vertical slice.

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
- exact-match Asset filtering;
- limit/offset pagination dengan validation;
- repository interface dan dependency injection;
- in-memory repository adapter;
- typed PostgreSQL configuration;
- PostgreSQL local service melalui Docker Compose;
- Psycopg database connectivity smoke test;
- database ADR dan manual API collection.
- Next.js 16 frontend dengan TypeScript dan App Router;
- typed frontend API client;
- interactive Asset dan Prediction form;
- explicit loading, success, dan error states;
- configurable CORS origins;
- PostgreSQL Asset repository;
- persisted Asset list;
- deterministic prediction stub;
- frontend lint, type-check, dan production build gates.


## Requirements

- Python 3.12 atau yang lebih baru
- Git
- Docker Desktop atau Docker Engine dengan Docker Compose
- Node.js 20.9 atau yang lebih baru
- npm

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

Install frontend dependencies:

```bash
cd web
npm install
cp .env.example .env.local
cd ..
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
Variabel backend:

- `APP_ENV`: `development`, `test`, atau `production`.
- `APP_DATA_DIR`: direktori penyimpanan file CSV.
- `APP_DATABASE_URL`: PostgreSQL connection string.
- `APP_CORS_ORIGINS`: daftar origin frontend yang dipisahkan koma.

Variabel frontend dalam `web/.env.local`:

- `NEXT_PUBLIC_API_BASE_URL`: alamat FastAPI yang digunakan browser.

File `.env` dan `web/.env.local` tidak boleh masuk Git. File `.env.example`
hanya berisi contoh konfigurasi aman.

## Local Run

```bash
production-summary readings.csv
```

expected output:

```text
columns: asset_id,value
rows: 2
```

Jika `APP_DATABASE_URL` tidak tersedia, database integration test akan
di-skip. Pada environment selain `test`, Asset API menggunakan PostgreSQL
jika `APP_DATABASE_URL` tersedia. Environment `test` tetap menggunakan
in-memory repository agar unit dan API tests terisolasi.

## HTTP API

Jalankan development server:

```bash
set -a
source .env
set +a

python3 -m uvicorn production_app.api.app:create_app \
  --factory \
  --reload \
  --host 127.0.0.1 \
  --port 8000
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
    "environment": "development"
}
```
## Web UI

Jalankan backend pada terminal pertama menggunakan command pada bagian
HTTP API.

Jalankan frontend pada terminal kedua:

```bash
cd web
npm run dev
```
Buka `http://localhost:3000`.

Dashboard menyediakan:

- form untuk membuat Asset;
- deterministic Prediction menggunakan readings;
- loading, success, dan error states;
- daftar Asset yang dibaca kembali dari PostgreSQL.

Frontend menggunakan `NEXT_PUBLIC_API_BASE_URL` dari `web/.env.local`.
Default development URL adalah `http://127.0.0.1:8000`.

## Local PostgreSQL

Jalankan PostgreSQL:

```bash
docker compose up -d postgres
```

Periksa health status:

```bash
docker compose ps
```

Service harus menampilkan status `healthy`.

Periksa database secara langsung:

```bash
docker compose exec postgres \
  psql \
  -U production_app \
  -d production_app \
  -c "SELECT current_database(), current_user;"
```

Jalankan Python database smoke test:

```bash
set -a
source .env
set +a

python3 -m pytest \
  tests/integration/test_database_connection.py \
  -v
```

Hentikan PostgreSQL tanpa menghapus data:

```bash
docker compose stop postgres
```

Named volume `postgres_data` menyimpan data ketika container dihentikan atau
dibuat ulang. Hindari `docker compose down -v` kecuali memang ingin menghapus
seluruh database lokal.

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
Filter menggunakan exact-match `asset_code`:

```http
GET /api/v1/assets?asset_code=PUMP-01
```

Pagination menggunakan `limit` dan `offset`:

```http
GET /api/v1/assets?limit=20&offset=0
```

| Parameter | Default | Constraint |
| --- | --- | --- |
| `asset_code` | null | exact match |
| `limit` | `20` | minimum `1`, maximum `100` |
| `offset` | `0` | minimum `0` |

Nilai pagination yang tidak valid menghasilkan `422 Unprocessable Content`.

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
git diff --check
```

Dengan PostgreSQL aktif dan `.env` termuat:

```text
70 passed
```

Tanpa `APP_DATABASE_URL`:

```text
69 passed, 1 skipped
```

Jalankan hanya unit/API tests tanpa integration test:

```bash
python3 -m pytest -m "not integration"
```

Jalankan database integration test:

```bash
python3 -m pytest -m integration -v
```

## Project structure

```text
.
├── data/
│   └── readings.csv
├── docs/
│   ├── adr/
│   │   └── 0001-postgresql-foundation.md
│   ├── http/
│   │   └── api.http
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
│       ├── database/
│       │   ├── connection.py
│       │   └── schema.py
│       ├── domain/
│       │   └── entities.py
│       ├── repositories/
│       │   ├── assets_repo.py
│       │   ├── in_memory_assets.py
│       │   └── postgres_assets.py
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
│   │   ├── test_cors.py
│   │   ├── test_health.py
│   │   └── test_predictions.py
│   ├── integration/
│   │   ├── test_asset_persistence.py
│   │   └── test_database_connection.py
│   ├── repositories/
│   │   └── test_in_memory_assets.py
│   ├── services/
│   │   ├── test_asset_service_repository.py
│   │   └── test_assets.py
│   ├── test_cli.py
│   ├── test_config.py
│   └── test_csv_summary.py
├── web/
│   ├── public/
│   ├── src/
│   │   ├── app/
│   │   │   ├── globals.css
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── components/
│   │   │   ├── persisted-assets.tsx
│   │   │   └── production-dashboard.tsx
│   │   └── lib/
│   │       └── api.ts
│   ├── .env.example
│   ├── eslint.config.mjs
│   ├── next.config.ts
│   ├── package-lock.json
│   ├── package.json
│   ├── postcss.config.mjs
│   └── tsconfig.json
├── .env.example
├── .gitignore
├── compose.yaml
├── pyproject.toml
└── README.md
```

## CSV contract

CSV valid harus memenuhi ketentuan berikut:

- memiliki header row;
- nama kolom tidak boleh kosong atau hanya berisi spasi;
- nama kolom tidak boleh duplikat setelah whitespace dihapus;
- setiap row harus memiliki jumlah value yang sama dengan jumlah kolom;
- row tidak boleh kekurangan value;
- row tidak boleh memiliki value tambahan.

Contoh CSV valid:

```csv
asset_id,value
A-01,10
A-02,20
```

Contoh header tidak valid:

```csv
asset_id,
A-01,10
```

Contoh row kekurangan value:

```csv
asset_id,value
A-01
```

Contoh row memiliki value tambahan:

```csv
asset_id,value
A-01,10,unexpected
```

Pada tahap saat ini, ingestion memvalidasi struktur CSV. Tipe atau makna
setiap value belum divalidasi oleh `csv_summary`.