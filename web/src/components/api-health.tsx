"use client";

import { useEffect, useState } from "react";
import { ApiRequestError, getHealth } from "@/lib/api";

type HealthState =
  | { status: "loading" }
  | { status: "success"; data: { environment: string } }
  | { status: "error"; message: string };

export default function ApiHealth() {
  const [state, setState] = useState<HealthState>({
    status: "loading",
  });

  useEffect(() => {
    getHealth()
      .then((data) => {
        setState({
          status: "success",
          data: {
            environment: data.environment,
          },
        });
      })
      .catch((error: unknown) => {
        const message =
          error instanceof ApiRequestError
            ? error.message
            : "Backend health check failed.";

        setState({
          status: "error",
          message,
        });
      });
  }, []);

  return (
    <div className="w-full max-w-sm rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-slate-700">API Health</span>

        {/* Status Badge */}
        {state.status === "loading" && (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-medium text-slate-600">
            <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-slate-400" />
            Checking
          </span>
        )}

        {state.status === "success" && (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-medium text-emerald-700">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
            Online
          </span>
        )}

        {state.status === "error" && (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-rose-50 px-2.5 py-0.5 text-xs font-medium text-rose-700">
            <span className="h-1.5 w-1.5 rounded-full bg-rose-500" />
            Offline
          </span>
        )}
      </div>

      {/* Detail Content */}
      <div className="mt-3 text-xs text-slate-500">
        {state.status === "loading" && <p>Checking backend connection...</p>}

        {state.status === "success" && (
          <p>
            Environment:{" "}
            <span className="font-semibold text-slate-800 capitalize">
              {state.data.environment}
            </span>
          </p>
        )}

        {state.status === "error" && (
          <p className="text-rose-600">{state.message}</p>
        )}
      </div>
    </div>
  );
}
