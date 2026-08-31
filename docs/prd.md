## Product Principles
Sebelum mendefinisikan fitur, pengembangan sistem ini berpegang pada prinsip-prinsip berikut:
- **Local-first:** Menjaga keamanan data industri agar tidak terekspos ke luar jaringan.
- **Explainable result:** Keputusan atau *risk score* tidak boleh menjadi *black box*; harus ada alasan yang jelas.
- **Evidence-based:** Setiap jawaban terkait SOP dari asisten AI harus memiliki sumber atau sitasi.
- **Deterministic:** Semua model harus dapat diuji secara konsisten dengan *fixture* deterministik.
- **Offline-capable:** Sistem harus tetap berguna dan dapat berjalan tanpa koneksi *cloud*.

## Masalah dan Pengguna
Tim produksi sering kali harus berpindah antara *spreadsheet*, catatan mesin, SOP, dan hasil inspeksi visual. Prototipe ini menyatukan ringkasan data, *risk alert*, *evidence-based assistant*, serta inspeksi gambar ke dalam satu antarmuka lokal.

Target pengguna sistem ini meliputi: **Operator, Maintenance Analyst, Quality Engineer, dan Supervisor.**

## 5.3 User Stories
- **Sebagai Supervisor**, saya ingin melihat tren produksi dan *alert* agar dapat memprioritaskan investigasi.
- **Sebagai Maintenance Analyst**, saya ingin melihat *risk score* beserta faktor pemicunya agar keputusan tidak menjadi *black box*.
- **Sebagai Administrator**, saya ingin dapat melakukan konfigurasi lokal tanpa menyimpan *secret* di dalam *repository*.
- **Sebagai Quality Engineer**, saya ingin mengunggah gambar dan melihat lokasi/tingkat anomali. *(Akan diimplementasikan pasca-MVP)*
- **Sebagai Operator**, saya ingin bertanya tentang SOP dan menerima jawaban beserta sumber aslinya. *(Akan diimplementasikan pasca-MVP)*

## Ruang Lingkup MVP (Scope)
Untuk memastikan iterasi pertama berjalan cepat dan stabil, pengembangan dibagi berdasarkan prioritas cakupan:

### MVP Scope (Fase Pertama):
- *Ingestion* untuk data aset dan produksi.
- *Baseline* tabular untuk sistem *predictive maintenance*.
- Pembuatan *risk score* dan penjabaran faktor pemicu.
- Dasbor (*dashboard*) produksi.
- Persistensi data menggunakan PostgreSQL.
- *Versioning* API dan pembuatan pengujian otomatis (*automated tests*).

> **Catatan:** Fitur *computer vision*, RAG, *local LLM*, dan *voice assistant* baru akan dikembangkan setelah alur inti (*core MVP*) di atas stabil.

### Out of Scope (Di Luar Cakupan MVP):
- *Deployment* ke *cloud* publik.
- Kontrol mesin secara otonom (*autonomous machine control*).
- Eksekusi keputusan *maintenance* secara otomatis tanpa validasi manusia.
- *Training* model kelas produksi dalam skala besar.
- *Voice assistant* sebagai fitur wajib.

## Fitur dan Non-Functional Requirements
Kebutuhan teknis dan fitur pendukung dibagi ke dalam beberapa kategori *non-functional* berikut:

| Kategori | Minimum Requirement | Tambahan (Nice-to-have) |
| :--- | :--- | :--- |
| **Isi (Content)** | Overview, production data, visual inspection, AI assistant, REST API, PostgreSQL, tabular risk, RAG+citation, OpenCV & vision result. | Voice input, provider switching, pgvector, Docker Compose, richer charts. |
| **Reliability** | *Deterministic seed* (jika relevan), *graceful errors*, *timeouts*, *health/readiness checks*. | - |
| **Security** | Validasi input, *upload allowlist/limit*, *safe filename*, CORS *allowlist*, *no secrets*, *parameterized queries*, *redacted logs*. | - |
| **Reproducibility** | *Pinned dependencies*, *migrations*, *data/model cards*, *checksums*, *exact run commands*. | - |
| **Performance** | *Benchmark latency/memory*, *lazy model loading/caching*, tidak ada *heavy inference* bersamaan secara *default*. | - |
| **Accessibility** | Alur dasar yang *keyboard-usable*, kontras warna yang mudah dibaca, label elemen, teks status yang eksplisit. | - |
| **Privacy** | Hanya menggunakan dataset publik/sintetis; **tidak ada** data pribadi atau data industri rahasia. | - |

## 5.6 Definition of Done (DoD)
Sebuah tugas atau fitur dianggap selesai **hanya jika** memenuhi seluruh kriteria berikut:
1. Kode telah terintegrasi (*merged*).
2. *Acceptance test* lulus dengan baik.
3. Output (UI/API) dapat dibuka dan diverifikasi.
4. Dokumentasi teknis/pengguna telah diperbarui.
5. *Commit* dibuat dengan pesan yang bermakna.
6. Keterbatasan sistem (jika ada) telah dicatat.
