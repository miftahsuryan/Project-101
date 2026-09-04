# Development Log

## D01 -  Engineering baseline
## Objective

membuat fondasi repository Python yang dapat diinstal, diuji, diperiksa tipenya, dan dikembangkan secara bertahap.

## Decisions

- Menggunakan Python 3.12.
- Menggunakan struktur 'src/' untuk memisahkan package dari root proyek.
- menggunakan 'pyproject.toml' sebagai pusat konfigurasi.
- menggunakan pytest untuk behavior
- Menggunkaan mypy dengan mode strict untuk static type checking
- menggunakan editable installation selama development

### Implemented

- Repository Git dengan branch utama 'main'.
- virtual environtment lokal
- package 'production_app'.
- model hasil 'CsvSummary'.
- fungsi 'summarize_csv()'.
- test untuk CSV valid.

## Verification

``` bash
python3 -m pytest
python3 -m ruff check src tests
python3 -m ruff format --check src tests
python3 -m mypy
```

## D02 - Typed ingestion foundation

### Objective

membuat ingestion service bertipe, validasi CSV, environment configuration, dan local run path

### Decisions

- Expected application errors memakai custom Exception `ProductionAppError`
- CSV invalid akan menggunakan exception class `CsvIngestionError`
- Konfigurasi Invalid akan menggunakan class `ConfigError`
- Environtment dibatasi ke `development`, `test`, atau `production`
- CLI bertindak sebagai adapter; aturan ingestion tetap berada di service
- Domain error menghasilkan stderr dan exit code `1`.

### Implemented

- Service boundary dalam `production_app.services`.
- Validasi header kosong dan duplikat.
- Validasi baris/row yang valuenya kurang atau berlebih.
- Translation `FileNotFoundError` ke `CSVIngestionError` sebagai interface ke user
- Typed `AppConfig` untuk konfigurasi Environment dan Directory data.
- Command `production-summary` untuk run local (CLI)
- `.env.example` dan sample data CSV.

### Verification

```bash
python3 -m ruff format src tests
python3 -m pytest
python3 -m ruff check src tests
python3 -m ruff format --check src tests
python3 -m mypy
```

manual valid path:

```bash
APP_ENV=development APP_DATA_DIR=./data \
production-summary readings.csv
```

manual invalid path:

```bash
APP_ENV=development APP_DATA_DIR=./data \
production-summary missing.csv
```

### known limitations

- Belum tersedia HTTP API
- Belum tersedia database
- Isi nilai CSV belum mempunyai domain schema
- File `.env` belum dimuat otomatis oleh aplikasi

## D03 - Versioned HTTP API

## Objective

membuat FastAPI application factory, versioned health endpoint, response chema, dan local HTTPP run path

### Decisions

- Menggunakan application factory `create_app()`
- Menempatkan endpoint di bawah prefix `/api/v1`
- Menggunakan Pydantic sebagao response schemma.
_ Menggunakan router factory agar config diberikan secara eksplisit
- Menggunakan Uvicorn sebagai ASGI development server.
- Menggunakan `Testclient` dengan `httpx22` untuk API testing
- Route tanpa version prefix harus menghasilkan `404`

### Implemented

- Package `production_app.api`
- `HealthResponse` schema
- `GET /api/v1/health`
- OpenAPI contract di `/openapi.json`
- Swagger UI di `/docs/`
- Test sstatus code, JSON response, version coundary, dan OpenAPI schema

### Verification

```bash
python3 -m pytest
python3 -m ruff check --no-cache src tests
python3 -m ruff format --check --no-cache src tests
python3 -m mypy
```

manual HTTP verification:

```bash
curl -i http://127.0.0.1:8000/api/v1/health
curl -i http://127.0.0.1:8000/health
```

expected behavior:
- versioned health endpoint menghasilkan `200`
- unversioned health endpoint menghasilkan `404`
- health response mengikuti `HealthResponse`
- OpenAPI mereferensikan schema `HealthResponse`

### Known Limitations

- health endpoint belum memeriksa database
- belum tersedia global API error evelope
- belum tersedia requst validation selain schema bawaan
- Belum tersedia production domain endpoint

## D04 - Production API contract

### Objective

Mendefinisikan typed prediction API contract, request validation, cosistent error envelope, dan fake prediction service.

### Decisions

- Menggunakan Pydantic untuk request dan response schema.
- MEnggunakan 'ErrorResponse' untuk validation dan domain errors.
- Request schema invalid menghasilkan status `422`.
- Request schema invalid menghasilkan status `409`.
- `RequestValidationError` diterjemahkkan global exception handler.
- Domain exception dipisahkan dari API response schema.
- Runtime handler dan OpenAPI response documentation didefinisikan terpisah

### Implemented

- `PredictionRequest` dan `PredictionResponse`.
- `ErrorDetail`, `ErrorBody`, dan `ErrorResponse`.
- Fake prediction service.
- `POST /api/v1/predictions`.
- Global request-validation handler.
- `PredictionUnvailableError` handler.
- OpenAPI contracts untuk status `200`, `409`, dan `422`.

### Verification

```bash
python3 -m pytest
python3 -m ruff check --no-cache src tests
python3 -m ruff format --check --no-cache src tests
python3 -m mypy
```

Expected Result:

- valid prediction request menghasil;kan `200`;
- invalid request schema menghasilkan `4212`;
- unavailable prediction menghasilkan `409`;
- seluruh error memakai top-level key `error`;
- openAPI menggunakan `ErrorResponse` untuk status `409`dan `422`.

### Known Limitations

- Prediction service masih menghasilkan canned value `0.0`
- aset dan reading belum disimpan
- belum tersedia CRUD asset
- belum terseda databse repository


## D05 - Production service boundary

### Objective

Membangun CRUD asset berbasis in-memory service, memisahkan domain dari HTTP,
dan mendefinisikan rancangan relasional awal untuk asset, reading, dan
prediction.

### Decisions

- Menggunakan immutable domain entity `Asset` berbasis frozen dataclass.
- Menggunakan UUID sebagai identifier internal asset.
- Menggunakan `asset_code` sebagai unique business identifier.
- Menempatkan aturan bisnis CRUD pada `InMemoryAssetService`.
- Menggunakan primary dictionary untuk pencarian berdasarkan UUID.
- Menggunakan secondary index untuk menjaga keunikan `asset_code`.
- Menggunakan router factory agar satu service instance dapat diberikan secara
  eksplisit kepada seluruh asset routes.
- Menerjemahkan domain exception menjadi HTTP error envelope melalui global
  exception handlers.
- Menggunakan `204 No Content` untuk penghapusan yang berhasil.
- Mendefinisikan ERD v0 sebelum membuat database schema dan migrations.

### Implemented

- Immutable `Asset` domain entity.
- `InMemoryAssetService` dengan operasi create, list, get, update, dan delete.
- `AssetNotFoundError`.
- `AssetCodeAlreadyExistsError`.
- Pydantic schemas `AssetCreate`, `AssetUpdate`, dan `AssetResponse`.
- `POST /api/v1/assets`.
- `GET /api/v1/assets`.
- `GET /api/v1/assets/{asset_id}`.
- `PUT /api/v1/assets/{asset_id}`.
- `DELETE /api/v1/assets/{asset_id}`.
- Error responses konsisten untuk status `404`, `409`, dan `422`.
- OpenAPI documentation untuk asset CRUD.
- Service tests dan API tests untuk happy path serta invalid path.
- ERD v0 pada `docs/erd-v0.md`.

### HTTP contract

| Method | Path | Success | Error |
| --- | --- | --- | --- |
| `POST` | `/api/v1/assets` | `201` | `409`, `422` |
| `GET` | `/api/v1/assets` | `200` | - |
| `GET` | `/api/v1/assets/{asset_id}` | `200` | `404`, `422` |
| `PUT` | `/api/v1/assets/{asset_id}` | `200` | `404`, `409`, `422` |
| `DELETE` | `/api/v1/assets/{asset_id}` | `204` | `404`, `422` |

### Verification

```bash
python3 -m pytest
python3 -m ruff check --no-cache src tests
python3 -m ruff format --check --no-cache src tests
python3 -m mypy
git diff --check
```

Expected result:

- Seluruh 41 tests lulus.
- Ruff tidak menemukan lint error.
- Seluruh source dan test files sudah terformat.
- Mypy tidak menemukan typing issue.
- Create, read, update, dan delete happy paths lulus.
- Duplicate `asset_code` menghasilkan `409`.
- Missing asset menghasilkan `404`.
- Invalid UUID dan invalid request menghasilkan `422`.
- Successful delete menghasilkan `204` tanpa response body.

### Relational design

ERD v0 mendefinisikan hubungan berikut:

- Satu asset dapat memiliki banyak readings.
- Satu asset dapat memiliki banyak predictions.
- Reading dan prediction mereferensikan UUID internal asset.
- Penghapusan asset yang masih memiliki data terkait direncanakan menggunakan
  `ON DELETE RESTRICT`.

Detail rancangan tersedia di [`erd-v0.md`](erd-v0.md).

### Known limitations

- Data asset masih disimpan dalam memory dan hilang ketika aplikasi restart.
- Service belum menggunakan repository interface.
- PostgreSQL connection dan database session belum tersedia.
- List assets belum memiliki pagination dan filtering.
- Reading dan prediction belum disimpan.
- Prediction API masih memakai string `asset_id` yang belum selaras dengan UUID
  internal pada domain asset.
- Database constraints dan transaction boundaries belum diterapkan.


## D06 - API behavior coverage and database foundation

### Objective

Menambahkan filter dan pagination pada Asset API, memisahkan service dari
persistence implementation, serta menyiapkan koneksi PostgreSQL yang dapat
diverifikasi melalui integration smoke test.

### Decisions

- Filter `asset_code` menggunakan exact match.
- List assets menggunakan offset-based pagination.
- Default `limit` adalah `20` dengan maksimum `100`.
- Default `offset` adalah `0` dan tidak boleh negatif.
- Route bergantung pada `AssetService`, bukan repository.
- `AssetService` bergantung pada `AssetRepository` Protocol.
- Dictionary storage dipindahkan ke `InMemoryAssetRepository`.
- PostgreSQL 17 dijalankan melalui Docker Compose.
- Psycopg 3 digunakan sebagai PostgreSQL driver.
- Database connection string dibaca dari `APP_DATABASE_URL`.
- `APP_DATABASE_URL` bersifat opsional selama runtime masih menggunakan
  in-memory repository.
- Database integration tests menggunakan marker `integration`.
- Schema tidak dibuat otomatis saat application startup.
- Versioned schema migrations ditunda sampai D09.

### Implemented

- Exact-match filtering pada `GET /api/v1/assets`.
- Pagination dengan query parameters `limit` dan `offset`.
- Runtime validation untuk pagination parameters.
- OpenAPI documentation untuk filter, pagination, dan `422 ErrorResponse`.
- `AssetRepository` Protocol.
- `InMemoryAssetRepository`.
- Constructor injection pada `AssetService`.
- Pemisahan business rules dari dictionary storage.
- PostgreSQL configuration melalui `APP_DATABASE_URL`.
- Validation untuk PostgreSQL URL.
- PostgreSQL 17 local service pada `compose.yaml`.
- Persistent PostgreSQL named volume.
- PostgreSQL container health check.
- Psycopg 3 binary dependency.
- `ping_database()` dengan query `SELECT 1`.
- PostgreSQL integration smoke test.
- Database architecture decision record.
- Manual API collection pada `docs/http/api.http`.

### Dependency direction

```text
FastAPI route
    → AssetService
        → AssetRepository Protocol
            ← InMemoryAssetRepository
            ← PostgreSQL repository (planned D08)
```

Business rules tetap berada pada service:

- missing asset menghasilkan `AssetNotFoundError`;
- duplicate asset code menghasilkan `AssetCodeAlreadyExistsError`;
- update mempertahankan UUID;
- delete memastikan asset tersedia sebelum repository dipanggil.

Persistence behavior berada pada repository:

- menyimpan dan mengambil entity;
- menjaga primary dan secondary indexes;
- menerapkan filter dan pagination;
- mengganti dan menghapus persisted entity.

### API query contract

| Parameter | Type | Default | Constraint |
| --- | --- | --- | --- |
| `asset_code` | string or null | null | exact match |
| `limit` | integer | `20` | minimum `1`, maximum `100` |
| `offset` | integer | `0` | minimum `0` |

Examples:

```http
GET /api/v1/assets?asset_code=PUMP-01
GET /api/v1/assets?limit=20&offset=0
```

Invalid pagination menghasilkan `422` menggunakan standard `ErrorResponse`
envelope.

### Database configuration

Local development URL:

```text
postgresql://production_app:production_app@localhost:5432/production_app
```

URL disediakan melalui environment variable dan tidak boleh dicetak ke log
karena dapat mengandung credentials.

Start PostgreSQL:

```bash
docker compose up -d postgres
docker compose ps
```

Manual database query:

```bash
docker compose exec postgres \
  psql \
  -U production_app \
  -d production_app \
  -c "SELECT current_database(), current_user;"
```

### Verification

Unit and API quality gate:

```bash
python3 -m pytest
python3 -m ruff check --no-cache src tests
python3 -m ruff format --check --no-cache src tests
python3 -m mypy
git diff --check
```

Explicit database smoke test:

```bash
set -a
source .env
set +a

python3 -m pytest \
  tests/integration/test_database_connection.py \
  -v
```

Expected result with PostgreSQL configured:

```text
70 passed
All checks passed!
Success: no issues found
```

Without `APP_DATABASE_URL`, the database integration test di-skip dan unit
suite tetap dapat dijalankan:

```text
69 passed, 1 skipped
```

### Deliverables

- API filter and pagination tests.
- Repository interface and in-memory adapter.
- Typed database configuration.
- PostgreSQL Docker Compose service.
- Database connectivity smoke test.
- ADR `docs/adr/0001-postgresql-foundation.md`.
- API collection `docs/http/api.http`.

### Known limitations

- Runtime Asset API masih menggunakan `InMemoryAssetRepository`.
- Asset data belum dipersist ke PostgreSQL.
- PostgreSQL repository belum tersedia.
- Connection/session belum menggunakan request-scoped dependency.
- Connection pooling belum tersedia.
- Transaction boundary baru didokumentasikan dan belum diterapkan ke CRUD.
- Database tables dan constraints belum dibuat.
- Alembic migrations belum tersedia.
- Offset pagination belum memiliki metadata seperti total row atau next page.

## D07 - Milestone v0.1 vertical slice

### Objective

Membuktikan satu alur MVP dari browser menuju FastAPI, PostgreSQL, dan kembali ke browser dengan deterministic prediction stub.

### Decisions

- Frontend menggunakan Next.js 16, TypeScript, App Router, dan Tailwind CSS.
- Static page tetap menjadi Server Component.
- Form dan persisted list menjadi Client Components karena membutuhkan state,
  event handler, dan browser-side fetch.
- Kontrak frontend ditulis manual berdasarkan schema dan contract test FastAPI.
- CORS origin dibaca dari `APP_CORS_ORIGINS`.
- Environment `test` tetap menggunakan in-memory repository agar test cepat
  dan terisolasi.
- Runtime development menggunakan PostgreSQL ketika `APP_DATABASE_URL`
  tersedia.
- Bootstrap schema D07 bersifat sementara sampai digantikan Alembic pada D09.

### Implemented

- Next.js application pada folder `web/`.
- Typed Asset dan Prediction API client.
- Form dengan idle, loading, success, dan error states.
- Deterministic prediction response menggunakan model `fake-v1`.
- Configurable CORS middleware.
- PostgreSQL Asset table bootstrap.
- `PostgresAssetRepository`.
- Composition root untuk memilih repository.
- Persisted Asset list pada frontend.
- Integration test yang membuat ulang application instance.
- Frontend lint, type-check, dan production build quality gate.

### Vertical slice

```text
Next.js form
    → typed API client
        → FastAPI route
            → AssetService
                → AssetRepository Protocol
                    → PostgreSQL adapter
                        → persisted Asset row

FastAPI prediction route
    → deterministic fake-v1 prediction
        → React success state
```
### Verification

Backend:

```bash
python3 -m pytest -m "not integration"
python3 -m ruff check .
python3 -m mypy
```
PostgreSQL integration:
```bash
set -a
source .env
set +a

python3 -m pytest tests/integration -v
```

Frontend:
```bash
cd web
npm run check
```
### Retrospective
- Origin frontend dan backend yang berbeda membutuhkan kontrak CORS eksplisit.
- Repository Protocol membuat service dapat berpindah dari memory ke PostgreSQL
  tanpa mengubah business rules.
- Membuat ulang application instance adalah cara sederhana untuk membuktikan
  persistence.
- Discriminated union mencegah kombinasi UI state yang tidak valid.
- Quality gate frontend dan backend perlu dijalankan secara terpisah dalam
  monorepo.

### Known limitations
- Setiap operasi repository membuka koneksi PostgreSQL baru.
- Belum tersedia connection pooling atau request-scoped lifecycle.
- Schema masih dibuat oleh bootstrap function, belum melalui Alembic.
- Prediction belum disimpan ke database.
- Persisted list diperbarui ketika halaman dimuat ulang.
- TypeScript API contract masih disinkronkan secara manual.
- Belum tersedia automated component test untuk frontend.

## D08 - Repository DB nyata

### Objective

Mengganti PostgreSQL repository berbasis koneksi langsung dengan repository
berbasis SQLAlchemy `Session` dan request-scoped transaction lifecycle.

### Implemented

- SQLAlchemy engine dan session factory.
- SQLAlchemy `AssetModel`.
- `PostgresAssetRepository` berbasis `Session`.
- Session dependency dengan commit dan rollback.
- Dependency service pada FastAPI assets router.
- In-memory repository tetap digunakan pada environment `test`.
- Integration test membuktikan asset tetap tersedia setelah application
  instance dibuat ulang.

### Verification

```text
71 passed, 2 skipped
ruff: All checks passed!
mypy: Success: no issues found
```

## D09 - Schema dan migrations

### Objective

Mengelola schema database menggunakan Alembic agar perubahan tabel dapat
dilacak, dijalankan, dan dibatalkan secara versioned.

### Implemented

- Alembic configuration pada `alembic.ini`.
- Migration environment pada `migrations/env.py`.
- `Base.metadata` terhubung ke Alembic.
- Migration awal untuk tabel `assets`.
- `upgrade()` untuk membuat tabel.
- `downgrade()` untuk menghapus tabel.
- Runtime API tidak lagi memanggil `ensure_asset_table()`.
- Bootstrap schema lama tidak lagi menjadi bagian dari application startup.

### Verification

Urutan berikut berhasil pada database kosong:

```bash
.venv/bin/alembic upgrade head
.venv/bin/alembic downgrade base
.venv/bin/alembic upgrade head
```

### Decision

Database schema dikelola oleh Alembic, bukan dibuat otomatis oleh aplikasi.
Hal ini membuat perubahan schema dapat direview dan direproduksi pada
environment berbeda.

### Next step

Menambahkan migration untuk tabel `readings` dan `predictions`, serta foreign key dan index berdasarkan ERD.


## D10 - Ingestion ke database

### Objective

Menyimpan reading dari CSV ke PostgreSQL secara bulk dan idempotent.

### Implemented

- Entity `Reading`.
- SQLAlchemy `ReadingModel`.
- Alembic migration untuk tabel `readings`.
- `ReadingRepository` protocol.
- `PostgresReadingRepository.add_many()`.
- `IngestService` untuk validasi, parsing, dan deduplication CSV.
- UUID deterministik menggunakan `uuid5`.
- `ON CONFLICT DO NOTHING` untuk mencegah duplicate saat re-import.
- CLI `production-ingest`.

### Data flow

```text
readings.csv
    → IngestService
        → Reading entity
            → PostgresReadingRepository
                → PostgreSQL
```

### Verification

```bash
python3 -m pytest -q
python3 -m ruff check src tests migrations
python3 -m mypy src
production-ingest readings.csv
production-ingest readings.csv
```

Import file yang sama dua kali tidak menggandakan row pada tabel `readings`.

### Decision

D10 menggunakan CLI sebagai production import entry point. Endpoint upload CSV
ditunda sampai diperlukan oleh frontend.

### Next step

D11 menambahkan typed web API client untuk menghubungkan Next.js dengan backend.


## D11 - Frontend typed client

### Objective

Menghubungkan Next.js dengan FastAPI melalui satu HTTP client yang typed,
sehingga bentuk request dan response dapat diperiksa sebelum runtime.

### Implemented

- TypeScript types untuk `HealthResponse`, `Asset`, `Prediction`, dan error envelope.
- Fungsi client `getHealth()`, `listAssets()`, `createAsset()`, dan `createPrediction()`.
- Konfigurasi URL backend melalui `NEXT_PUBLIC_API_BASE_URL`.
- `ApiRequestError` untuk menangani error HTTP.
- Komponen `ApiHealth` dengan state loading, success, dan error.

### Data flow

```text
Next.js component
    → web/src/lib/api.ts
        → HTTP /api/v1/*
            → FastAPI
```

### Verfication

```bash
cd web
npm run lint
npm run typecheck
npm run build
```

Dengan backend aktif, halaman web menampilkan status:

```text
API online — environment: development
```

Jika backend dihentikan, h

### Next Step

D12 menampilkan overview berbasis agregasi data nyata dari backend.


## D12 - Production overview

### Objective

Menampilkan ringkasan data produksi nyata dari PostgreSQL pada dashboard
Next.js.

### Implemented

- `OverviewResponse` sebagai kontrak API.
- `ReadingSummary` untuk agregasi jumlah, rata-rata, dan nilai terbaru.
- `AssetRepository.count()` untuk menghitung jumlah asset.
- `OverviewService` yang menggabungkan asset dan reading summary.
- Endpoint `GET /api/v1/overview`.
- Typed client `getOverview()` pada `web/src/lib/api.ts`.
- Komponen `OverviewCards` pada dashboard.
- Loading, success, dan error state untuk overview.

### Data flow

```text
PostgreSQL assets/readings
    → repositories
        → OverviewService
            → GET /api/v1/overview
                → getOverview()
                    → OverviewCards
```
### Example response
{
  "total_assets": 5,
  "total_readings": 2,
  "average_reading": 15.0,
  "latest_reading": 10.0
}

latest_reading saat ini ditentukan berdasarkan created_at database.

### Verfication
curl http://127.0.0.1:8000/api/v1/overview
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check src tests
.venv/bin/python -m mypy src
cd web
npm run lint
npx tsc --noEmit --incremental false
npm run build

### Next step

D13 menambahkan production table, filtering, dan pagination pada frontend.

## D13 - Production data explorer

### Objective

Menyediakan tabel readings pada frontend dengan filter asset code dan
pagination berbasis API.

### Implemented

- Endpoint `GET /api/v1/readings`.
- Filter exact-match berdasarkan `asset_code`.
- Pagination menggunakan `limit` dan `offset`.
- Typed client `listReadings()`.
- Production table pada Next.js.
- Loading, error, dan success state.
- Filter tidak mengirim request pada setiap karakter.
- Pagination tidak melakukan full page reload.
### Data flow

```text
PostgreSQL readings
    → PostgresReadingRepository.list_page()
        → ReadingService.list_readings()
            → GET /api/v1/readings
                → listReadings()
                    → ProductionTable
```

### Verification

```bash
curl "http://127.0.0.1:8000/api/v1/readings?limit=20&offset=0"
curl "http://127.0.0.1:8000/api/v1/readings?asset_code=A-01"
```

### Next step
D14 melengkapi UI state: loading, empty, error, dan success.

## D14 - Harden core UI states

### Objective

Memastikan seluruh UI inti dapat menangani loading, empty, error, dan success
state secara konsisten.

### Implemented

- Empty state pada `OverviewCards`.
- Empty state pada `ProductionTable`.
- Error dan loading state pada seluruh komponen utama.
- Validasi asset code, asset name, dan readings.
- Prediction menggunakan UUID asset.
- Layout tetap tampil saat request berjalan.
- Filter tidak melakukan request pada setiap karakter.
- Pagination tidak melakukan full page reload.

### Verification

```bash
.venv/bin/python -m pytest -q
.venv/bin/python -m ruff check src tests
.venv/bin/python -m mypy src

cd web
npm run lint
npx tsc --noEmit --incremental false
npm run build
```

### Next step

D15 membangun seed data deterministik dan tabular baseline untuk deteksi risiko kegagalan mesin.

## D15 - Tabular ML baseline and data seed

### Objective

Membangun dataset seed deterministik dan rule-based baseline untuk risiko kegagalan mesin dari dataset AI4I 2020 Predictive Maintenance sebagai pembanding awal sebelum model machine learning terkalibrasi.

### Decisions

- Menggunakan dataset industri publik `data/ai4i2020.csv` (10,000 records).
- Memisahkan identitas mesin (`UDI`, `Product ID`, `Type`) dari fitur numerik sensor (`Air temperature`, `Process temperature`, `Rotational speed`, `Torque`, `Tool wear`).
- Menggunakan deterministic heuristic formula (`baseline-v1`) tanpa dependensi framework external.
- Menyediakan perbandingan kuantitatif terhadap Naive Majority Baseline (Dummy Class 0).
- Membangun script generator seed deterministik (`scripts/seed_data.py`) yang menghasilkan subset representatif (mesin normal dan mesin berisiko) ke dalam CSV dan database.

### Implemented

- Service `RiskBaselineService` pada `src/production_app/services/risk_baseline.py`.
- Script evaluasi metrik `scripts/evaluate_baseline.py` dengan perbandingan Naive vs Baseline-v1 serta evaluasi split 80/20 train/test.
- Script data seed `scripts/seed_data.py` untuk pembuatan `data/seed_assets.csv` dan `data/seed_readings.csv`.
- Unit tests `tests/services/test_risk_baseline.py` dan `tests/test_seed_data.py`.
- Dokumentasi tabular baseline dan metrik pada `docs/ml-baseline.md`.

### Evaluation Summary

| Model / Split | Total Rows | Accuracy | Precision | Recall | F1-Score | TP | FP | FN | TN |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Naive (Dummy Class 0)** | 10,000 | 96.61% | 0.00% | 0.00% | 0.0000 | 0 | 0 | 339 | 9,661 |
| **Baseline-v1 (Full)** | 10,000 | 96.98% | 79.37% | 14.75% | 0.2488 | 50 | 13 | 289 | 9,648 |
| **Baseline-v1 (Train 80%)** | 8,000 | 96.65% | 84.78% | 13.00% | 0.2254 | 39 | 7 | 261 | 7,693 |
| **Baseline-v1 (Test 20%)** | 2,000 | 98.30% | 64.71% | 28.21% | 0.3929 | 11 | 6 | 28 | 1,955 |

### Verification

```bash
PYTHONPATH=src .venv/bin/python scripts/evaluate_baseline.py
PYTHONPATH=src .venv/bin/python scripts/seed_data.py
.venv/bin/python -m pytest tests/services/test_risk_baseline.py tests/test_seed_data.py -q
.venv/bin/python -m ruff check src tests scripts
.venv/bin/python -m mypy src tests scripts
```

### Next step

D16 membungkus baseline ke dalam risk service terintegrasi API dan menyusun evidence index portofolio recruiter.
,
