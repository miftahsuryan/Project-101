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

Evaluasi awal menggunakan seluruh row dataset:

```text
rows: 10000
true_positive: 50
true_negative: 9648
false_positive: 13
false_negative: 289
accuracy: 0.9698
```
## Interpretation

Baseline ini digunakan sebagai reference point. Nilai accuracy bukan satu-satunya
metrik penting karena dataset memiliki jumlah failure yang jauh lebih sedikit
dibandingkan non-failure.

False negative perlu diperhatikan karena berarti mesin berisiko tetapi tidak
terdeteksi oleh baseline.

Angka di atas adalah baseline awal dan belum menunjukkan performa model
production.


Catatan penting: baseline menganggap `risk_level == "high"` sebagai prediksi
kegagalan. Ini aturan sederhana untuk pembanding, bukan model klasifikasi final.

Jalankan quality check:

```bash
.venv/bin/python -m ruff check src tests scripts
.venv/bin/python -m mypy src
.venv/bin/python -m pytest -q
```
