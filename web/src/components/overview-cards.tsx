"use client";

import { useEffect, useState } from "react";

import { ApiRequestError, getOverview, type OverviewResponse } from "@/lib/api";

type OverviewState =
  | { status: "loading" }
  | { status: "success"; data: OverviewResponse }
  | { status: "error"; message: string };

export default function OverviewCards() {
  const [state, setState] = useState<OverviewState>({
    status: "loading",
  });

  useEffect(() => {
    getOverview()
      .then((data) => {
        setState({ status: "success", data });
      })
      .catch((error: unknown) => {
        setState({
          status: "error",
          message:
            error instanceof ApiRequestError
              ? error.message
              : "Failed to load overview.",
        });
      });
  }, []);

  if (state.status === "loading") {
    return (
      <p className="text-sm text-slate-500">
        Loading overview...
      </p>
    );
  }

  if (state.status === "error") {
    return (
      <p className="text-sm text-rose-700">
        Overview unavailable: {state.message}
      </p>
    );
  }

  const { data } = state;

  const hasNoData =
    data.total_assets === 0 &&
    data.total_readings === 0;

  if (hasNoData) {
    return (
      <section className="rounded-xl border border-dashed border-slate-300 bg-white p-8 text-center">
        <p className="font-medium text-slate-700">
          No overview data available
        </p>

        <p className="mt-1 text-sm text-slate-500">
          Add assets or import readings to see the summary.
        </p>
      </section>
    );
  }

  return (
    <section className="grid gap-4 sm:grid-cols-2">
      <OverviewCard
        label="Total assets"
        value={data.total_assets}
      />
      <OverviewCard
        label="Total readings"
        value={data.total_readings}
      />
      <OverviewCard
        label="Average reading"
        value={data.average_reading ?? "—"}
      />
      <OverviewCard
        label="Latest reading"
        value={data.latest_reading ?? "—"}
      />
    </section>
  );
}

type OverviewCardProps = {
  label: string;
  value: number | string;
};

function OverviewCard({ label, value }: OverviewCardProps) {
  return (
    <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-bold text-slate-900">
        {value}
      </p>
    </article>
  );
}