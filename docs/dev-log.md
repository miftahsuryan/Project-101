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