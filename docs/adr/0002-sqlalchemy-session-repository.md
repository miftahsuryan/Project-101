# ADR 0002: SQLAlchemy session dan PostgreSQL repository

- Status: Accepted
- Date: 2026-08-29

## Context

D07 menggunakan PostgreSQL repository berbasis koneksi Psycopg langsung.
Pendekatan tersebut belum memiliki request-scoped session dan transaction
boundary yang dikelola oleh aplikasi.

D08 membutuhkan repository yang terintegrasi dengan SQLAlchemy serta lifecycle
session yang jelas pada setiap request API.

## Decision

- Menggunakan SQLAlchemy 2.x sebagai ORM dan database abstraction.
- Menggunakan Psycopg 3 sebagai PostgreSQL driver.
- `AssetModel` merepresentasikan tabel `assets`.
- `PostgresAssetRepository` menerima SQLAlchemy `Session`.
- Repository tidak melakukan `commit` sendiri.
- FastAPI session dependency melakukan:
  - `commit` jika request berhasil;
  - `rollback` jika terjadi exception;
  - menutup session setelah request selesai.
- Environment `test` tetap menggunakan `InMemoryAssetRepository`.
- Environment selain `test` menggunakan PostgreSQL jika
  `APP_DATABASE_URL` tersedia.

## Dependency direction

```text
FastAPI route
    → AssetService
        → AssetRepository Protocol
            ← InMemoryAssetRepository
            ← PostgresAssetRepository
                → SQLAlchemy Session
                    → PostgreSQL
```

Service dan domain tidak bergantung pada FastAPI atau SQLAlchemy.

## Transaction boundary

```text
request masuk
    → buka session
    → jalankan service dan repository
    → commit jika berhasil
    → rollback jika gagal
    → tutup session
```

## Consequences

### Positive

- Lifecycle database connection lebih terkontrol.
- Repository dapat diuji tanpa menjalankan PostgreSQL.
- Business rule tetap berada pada service.
- Implementasi memory dan PostgreSQL mengikuti protocol yang sama.
- Transaction boundary terlihat jelas.

### Negative

- PostgreSQL tetap diperlukan untuk integration test.
- Session dependency perlu dikonfigurasi pada composition root.
- Migration database belum tersedia.

## Deferred work

- Mengganti `ensure_asset_table()` dengan Alembic.
- Menambahkan migration upgrade dan downgrade.
- Menambahkan transaction integration test yang lebih lengkap.
- Menambahkan tabel readings dan predictions.