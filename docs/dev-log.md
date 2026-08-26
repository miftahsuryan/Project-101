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
