# Tabular ML Baseline

## Tujuan

Membuat baseline risiko kerusakan mesin yang sederhana, deterministik, dan
mudah dijelaskan sebelum menggunakan model machine learning yang lebih kompleks.

Baseline digunakan sebagai pembanding awal, bukan sebagai model production final.

## Dataset

Dataset yang digunakan:

```text
AI4I 2020 Predictive Maintenance Dataset
```

File:

```text
data/ai4i2020.csv
```

Target prediksi:

```text
Machine failure
```

Target bernilai:

```text
0 = mesin tidak mengalami kegagalan
1 = mesin mengalami kegagalan
```

## Fitur Sensor

Baseline menggunakan fitur berikut:

- `Air temperature [K]`
- `Process temperature [K]`
- `Rotational speed [rpm]`
- `Torque [Nm]`
- `Tool wear [min]`

Kolom identitas seperti `UDI`, `Product ID`, dan `Type` tidak digunakan sebagai
fitur numerik baseline.

## Metode Baseline

Versi pertama menggunakan deterministic threshold score.

Contoh prinsip:

```text
tool wear tinggi       → risiko meningkat
torque tinggi          → risiko meningkat
rotational speed tidak normal → risiko meningkat
perbedaan temperatur besar → risiko meningkat
```

Input yang sama harus selalu menghasilkan output yang sama.

## Output

```json
{
  "risk_score": 0.42,
  "risk_level": "medium",
  "model_version": "baseline-v1"
}
```

Level risiko:

```text
0.00 - 0.33 → low
0.34 - 0.66 → medium
0.67 - 1.00 → high
```

## Kontrak Service

Service menerima nilai fitur sensor:

```text
air_temperature
process_temperature
rotational_speed
torque
tool_wear
```

Service mengembalikan:

```text
risk_score
risk_level
model_version
```

Service tidak bergantung pada FastAPI, PostgreSQL, atau frontend.

## Reproducibility

Baseline harus:

- menghasilkan output yang sama untuk input yang sama;
- memiliki versi model;
- memiliki test untuk nilai normal;
- memiliki test untuk nilai berisiko tinggi;
- menggunakan aturan yang terdokumentasi.

## Batasan

Baseline ini belum digunakan untuk keputusan produksi. Hasilnya hanya digunakan
sebagai pembanding awal untuk model machine learning berikutnya.

Baseline belum memberikan:

- probabilitas terkalibrasi;
- feature importance;
- explainable AI formal;
- evaluasi cross-validation;
- deployment model production.

## Rencana Pengembangan

Tahap berikutnya:

1. membuat deterministic baseline service;
2. menambahkan unit test;
3. mengukur precision, recall, dan accuracy;
4. membandingkan dengan dummy classifier;
5. mencoba logistic regression;
6. menyimpan metadata model dan versi artifact.

## Baseline Metrics

Evaluasi perbandingan antara Naive Majority Baseline (Dummy Classifier yang selalu memprediksi tidak gagal) dan Deterministic Heuristic Baseline (`baseline-v1` di mana `risk_level == "high"` dianggap gagal):

| Model / Split | Total Rows | Accuracy | Precision | Recall | F1-Score | TP | FP | FN | TN |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Naive (Dummy Class 0)** | 10,000 | 96.61% | 0.00% | 0.00% | 0.0000 | 0 | 0 | 339 | 9,661 |
| **Baseline-v1 (Full)** | 10,000 | 96.98% | 79.37% | 14.75% | 0.2488 | 50 | 13 | 289 | 9,648 |
| **Baseline-v1 (Train 80%)** | 8,000 | 96.65% | 84.78% | 13.00% | 0.2254 | 39 | 7 | 261 | 7,693 |
| **Baseline-v1 (Test 20%)** | 2,000 | 98.30% | 64.71% | 28.21% | 0.3929 | 11 | 6 | 28 | 1,955 |

## Interpretation

1. **Ilusi Accuracy pada Imbalanced Dataset:**
   - Naive baseline mencapai akurasi 96.61% tanpa memprediksi satupun kegagalan (`recall = 0.00%`). Jika hanya melihat akurasi, model tampak prima padahal 100% kerusakan mesin terlewatkan.
2. **Kekuatan Heuristic Baseline-v1:**
   - Dengan precision 79.37%, hampir 80% dari alarm yang dikeluarkan terbukti merupakan kerusakan nyata dengan false alarm sangat rendah (hanya 13 false positive).
   - Menangkap 50 kerusakan mesin nyata pada dataset penuh dan 11 pada test set (F1 test: 0.3929).
3. **Peluang Iterasi Berikutnya:**
   - False negative (289 pada full dataset) menunjukkan masih banyak failure modes (seperti kegagalan akibat overload mendadak atau power failure) yang memerlukan model terkalibrasi atau feature engineering lanjutan (logistic regression / tree-based classifier).

## Deterministic Data Seeding

Tersedia script `scripts/seed_data.py` untuk mengekstrak sampel realistis dan deterministik dari `data/ai4i2020.csv`:

```bash
PYTHONPATH=src .venv/bin/python scripts/seed_data.py
```

Output:
- `data/seed_assets.csv`: Daftar asset terformat (`asset_code,name`).
- `data/seed_readings.csv`: Readings kompatibel dengan ingest service (`asset_id,value`).
- Opsi `--load-db` untuk langsung mengisi database PostgreSQL lokal saat `APP_DATABASE_URL` aktif.

Jalankan quality check:

```bash
.venv/bin/python -m ruff check src tests scripts
.venv/bin/python -m mypy src tests scripts
.venv/bin/python -m pytest -q
```

