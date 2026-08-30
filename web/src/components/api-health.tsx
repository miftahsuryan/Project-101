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

  if (state.status === "loading") {
    return <p className="text-sm text-slate-500">Checking API...</p>;
  }

  if (state.status === "error") {
    return (
      <p className="text-sm text-red-700">
        API unavailable: {state.message}
      </p>
    );
  }

  return (
    <p className="text-sm text-emerald-700">
      API online — environment: {state.data.environment}
    </p>
  );
}