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
