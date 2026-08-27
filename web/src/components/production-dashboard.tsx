"use client";

import type { FormEvent } from "react";
import { useState } from "react";

import {
  createAsset,
  createPrediction,
  type Asset,
  type Prediction,
} from "@/lib/api";

type SubmissionState =
  | { status: "idle" }
  | { status: "loading" }
  | {
      status: "success";
      asset: Asset;
      prediction: Prediction;
    }
  | {
      status: "error";
      message: string;
    };

export default function ProductionDashboard() {
  const [assetCode, setAssetCode] = useState("PUMP-01");
  const [assetName, setAssetName] = useState("Main Pump");
  const [readings, setReadings] = useState("10, 12");
  const [submission, setSubmission] =
    useState<SubmissionState>({ status: "idle" });

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    const parsedReadings = readings
      .split(",")
      .map((value) => value.trim())
      .filter((value) => value.length > 0)
      .map(Number);

    if (
      parsedReadings.length === 0 ||
      parsedReadings.some((value) => !Number.isFinite(value))
    ) {
      setSubmission({
        status: "error",
        message: "Readings harus berisi angka yang dipisahkan koma.",
      });
      return;
    }

    setSubmission({ status: "loading" });

    try {
      const asset = await createAsset({
        asset_code: assetCode.trim(),
        name: assetName.trim(),
      });

      const prediction = await createPrediction({
        asset_id: asset.asset_code,
        readings: parsedReadings,
      });

      setSubmission({
        status: "success",
        asset,
        prediction,
      });
    } catch (error: unknown) {
      setSubmission({
        status: "error",
        message:
          error instanceof Error
            ? error.message
            : "Terjadi error yang tidak diketahui.",
      });
    }
  }

  const isLoading = submission.status === "loading";

  return (
    <form
      className="grid gap-5 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
      onSubmit={handleSubmit}
    >
      <div className="grid gap-2">
        <label htmlFor="asset-code" className="font-medium">
          Asset code
        </label>
        <input
          id="asset-code"
          className="rounded-lg border border-slate-300 px-3 py-2"
          value={assetCode}
          onChange={(event) => setAssetCode(event.target.value)}
          disabled={isLoading}
          required
        />
      </div>

      <div className="grid gap-2">
        <label htmlFor="asset-name" className="font-medium">
          Asset name
        </label>
        <input
          id="asset-name"
          className="rounded-lg border border-slate-300 px-3 py-2"
          value={assetName}
          onChange={(event) => setAssetName(event.target.value)}
          disabled={isLoading}
          required
        />
      </div>

      <div className="grid gap-2">
        <label htmlFor="readings" className="font-medium">
          Readings
        </label>
        <input
          id="readings"
          className="rounded-lg border border-slate-300 px-3 py-2"
          value={readings}
          onChange={(event) => setReadings(event.target.value)}
          disabled={isLoading}
          placeholder="10, 12"
          required
        />
        <p className="text-sm text-slate-500">
          Pisahkan setiap nilai menggunakan koma.
        </p>
      </div>

      <button
        type="submit"
        className="rounded-lg bg-slate-900 px-4 py-3 font-medium text-white disabled:cursor-not-allowed disabled:bg-slate-400"
        disabled={isLoading}
      >
        {isLoading
          ? "Processing..."
          : "Create asset and prediction"}
      </button>

      {submission.status === "error" && (
        <p
          role="alert"
          className="rounded-lg bg-red-50 p-4 text-red-700"
        >
          {submission.message}
        </p>
      )}

      {submission.status === "success" && (
        <section className="grid gap-2 rounded-lg bg-emerald-50 p-4">
          <h2 className="font-semibold text-emerald-900">
            Prediction created
          </h2>

          <p>Asset: {submission.asset.asset_code}</p>
          <p>Asset ID: {submission.asset.id}</p>
          <p>
            Predicted value:{" "}
            {submission.prediction.predicted_value}
          </p>
          <p>
            Model: {submission.prediction.model_version}
          </p>
        </section>
      )}
    </form>
  );
}