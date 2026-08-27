"use client";

import { useEffect, useState } from "react";

import { listAssets, type Asset } from "@/lib/api";

type AssetListState =
  | { status: "loading" }
  | { status: "success"; assets: Asset[] }
  | { status: "error"; message: string };

export default function PersistedAssets() {
  const [state, setState] = useState<AssetListState>({
    status: "loading",
  });

  useEffect(() => {
    let cancelled = false;

    async function loadAssets() {
      try {
        const assets = await listAssets();

        if (!cancelled) {
          setState({
            status: "success",
            assets,
          });
        }
      } catch (error: unknown) {
        if (!cancelled) {
          setState({
            status: "error",
            message:
              error instanceof Error
                ? error.message
                : "Gagal mengambil asset.",
          });
        }
      }
    }

    void loadAssets();

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section className="grid gap-4 rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
      <div>
        <h2 className="text-xl font-semibold">
          Persisted assets
        </h2>
        <p className="text-sm text-slate-500">
          Data ini dibaca kembali dari backend.
        </p>
      </div>

      {state.status === "loading" && (
        <p className="text-slate-500">Loading assets...</p>
      )}

      {state.status === "error" && (
        <p
          role="alert"
          className="rounded-lg bg-red-50 p-4 text-red-700"
        >
          {state.message}
        </p>
      )}

      {state.status === "success" &&
        state.assets.length === 0 && (
          <p className="text-slate-500">
            Belum ada asset tersimpan.
          </p>
        )}

      {state.status === "success" &&
        state.assets.length > 0 && (
          <ul className="grid gap-3">
            {state.assets.map((asset) => (
              <li
                key={asset.id}
                className="rounded-lg border border-slate-200 p-4"
              >
                <p className="font-semibold">
                  {asset.asset_code}
                </p>
                <p className="text-slate-600">{asset.name}</p>
                <p className="mt-1 break-all text-xs text-slate-400">
                  {asset.id}
                </p>
              </li>
            ))}
          </ul>
        )}
    </section>
  );
}