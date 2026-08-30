## Product Principles

- Local-first untuk menjaga keamanan data industri.
- Explainable result, bukan hanya skor tanpa alasan.
- Setiap jawaban SOP harus memiliki sumber atau sitasi.
- Semua model harus dapat diuji dengan fixture deterministik.
- Sistem harus tetap berguna tanpa koneksi cloud.

## MVP Scope

MVP pertama memprioritaskan:

- Asset dan production data ingestion;
- predictive maintenance tabular baseline;
- risk score dan faktor pemicu;
- dashboard production;
- persistence PostgreSQL;
- API versioning dan automated tests.

Fitur computer vision, RAG, local LLM, dan voice assistant dikembangkan setelah
alur core MVP stabil.

## Out of Scope for Initial MVP

- Deployment cloud publik;
- autonomous machine control;
- keputusan maintenance tanpa validasi manusia;
- production-grade model training skala besar;
- voice assistant sebagai fitur wajib.