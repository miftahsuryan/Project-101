# ADR 0001: PostgreSQL foundation

- Status: Accepted
- Date: 2026-08-27

## Context

Aplikasi membutuhkan persistent relational storage untuk asset, readings, dan
predictions. Implementasi in-memory saat ini hilang ketika proses aplikasi
berhenti dan tidak dapat menjamin relational constraints atau transaction
behavior.

D05 telah mendefinisikan domain entity, service boundary, CRUD API, dan ERD v0.
D06 membutuhkan database configuration, repository seam, dan connectivity
smoke test tanpa langsung mengimplementasikan seluruh ORM schema.

## Decision

- Menggunakan PostgreSQL 17 sebagai relational database.
- Menjalankan PostgreSQL lokal melalui Docker Compose.
- Menggunakan named volume agar data development tetap persisten.
- Menggunakan Psycopg 3 sebagai Python PostgreSQL driver.
- Membaca connection string dari `APP_DATABASE_URL`.
- Tidak menyimpan atau mencetak database credentials di source code dan log.
- Menggunakan `AssetRepository` Protocol sebagai persistence interface.
- Menggunakan `InMemoryAssetRepository` selama real PostgreSQL repository
  belum tersedia.
- Menempatkan business rules dan domain exceptions di `AssetService`.
- Menempatkan dictionary atau SQL implementation di repository adapter.
- Menandai test yang membutuhkan PostgreSQL dengan marker `integration`.
- Menggunakan `SELECT 1` sebagai database connectivity smoke test.

## Dependency direction

```text
FastAPI route
    → AssetService
        → AssetRepository Protocol
            ← InMemoryAssetRepository
            ← PostgreSQL repository (D08)
```

Lapisan domain dan service tidak boleh bergantung pada Psycopg, FastAPI, atau
implementasi database konkret.

## Transaction boundary

Write operation akan dijalankan dalam satu transaction:

```text
begin
    → repository operation
    → commit jika berhasil
    → rollback jika exception
```

Request-scoped connection atau session lifecycle akan diterapkan ketika real
PostgreSQL repository dibuat.

## Migration policy

Aplikasi tidak akan membuat tabel secara otomatis saat startup.

Schema changes akan dikelola melalui versioned Alembic migrations pada D09.
Migration harus dapat menjalankan urutan:

```text
upgrade
→ downgrade
→ upgrade
```

terhadap database kosong.

## Consequences

### Positive

- Penyimpanan dapat diganti tanpa mengubah route atau business rules.
- Unit tests tetap cepat menggunakan in-memory repository.
- Integration tests memverifikasi PostgreSQL secara nyata.
- Database credentials berasal dari environment.
- Schema evolution nantinya memiliki migration history.

### Negative

- Local development membutuhkan Docker.
- Integration test lebih lambat daripada unit test.
- In-memory dan PostgreSQL adapters harus mengikuti repository contract yang sama.
- Runtime production menggunakan PostgreSQL jika `APP_DATABASE_URL`
  tersedia.
- Environment `test` menggunakan in-memory repository untuk isolasi test.

## Deferred work

- Alembic migrations: D09.
- Database transaction integration tests yang lebih lengkap: D09.
- Tabel readings dan predictions: tahap lanjutan.

## Verification

```bash
docker compose up -d postgres
docker compose ps

set -a
source .env
set +a

python3 -m pytest tests/integration/test_database_connection.py -v
```

Expected result:

```text
PostgreSQL container is healthy
1 passed
``` 
