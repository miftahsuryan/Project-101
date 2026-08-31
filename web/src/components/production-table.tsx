"use client";

import {
  type FormEvent,
  useEffect,
  useState,
} from "react";

import {
  ApiRequestError,
  listReadings,
  type ReadingPage,
} from "@/lib/api";

const PAGE_SIZE = 20;

type ProductionState =
  | { status: "loading"; data: ReadingPage | null }
  | { status: "success"; data: ReadingPage }
  | { status: "error"; message: string; data: ReadingPage | null };

export default function ProductionTable() {
  const [filterInput, setFilterInput] = useState("");
  const [assetCode, setAssetCode] = useState("");
  const [offset, setOffset] = useState(0);

  const [state, setState] = useState<ProductionState>({
    status: "loading",
    data: null,
  });

  useEffect(() => {
    let ignore = false;

    async function fetchReadings() {
      setState((current) => ({
        status: "loading",
        data: current.data,
      }));

      try {
        const data = await listReadings(
          assetCode,
          PAGE_SIZE,
          offset,
        );

        if (!ignore) {
          setState({
            status: "success",
            data,
          });
        }
      } catch (error: unknown) {
        if (!ignore) {
          setState({
            status: "error",
            message:
              error instanceof ApiRequestError
                ? error.message
                : "Failed to load readings.",
            data: null,
          });
        }
      }
    }

    void fetchReadings();

    return () => {
      ignore = true;
    };
  }, [assetCode, offset]);

  function handleFilterSubmit(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();
    setOffset(0);
    setAssetCode(filterInput.trim());
  }

  const data = state.data;

  return (
    <section className="grid gap-4">
      <form
        onSubmit={handleFilterSubmit}
        className="flex gap-2"
      >
        <input
          value={filterInput}
          onChange={(event) => {
            setFilterInput(event.target.value);
          }}
          placeholder="Filter asset code"
          className="rounded border px-3 py-2"
        />

        <button
          type="submit"
          className="rounded bg-slate-900 px-4 py-2 text-white"
        >
          Filter
        </button>
      </form>

      {state.status === "loading" && (
        <p className="text-sm text-slate-500">
          Loading production readings...
        </p>
      )}

      {state.status === "error" && (
        <p className="text-sm text-rose-700">
          {state.message}
        </p>
      )}

      {data !== null && (
        <>
          <p className="text-sm text-slate-500">
            Showing {data.items.length} of {data.total} readings
          </p>

          <div className="overflow-x-auto rounded-xl border bg-white">
            <table className="min-w-full text-left text-sm">
              <thead className="border-b bg-slate-50">
                <tr>
                  <th className="px-4 py-3">Asset</th>
                  <th className="px-4 py-3">Value</th>
                </tr>
              </thead>

              <tbody>
                {data.items.map((reading) => (
                  <tr
                    key={reading.id}
                    className="border-b last:border-0"
                  >
                    <td className="px-4 py-3">
                      {reading.asset_code}
                    </td>
                    <td className="px-4 py-3">
                      {reading.value}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex gap-2">
            <button
              type="button"
              disabled={offset === 0}
              onClick={() => {
                setOffset(
                  Math.max(0, offset - PAGE_SIZE),
                );
              }}
              className="rounded border px-3 py-2 disabled:opacity-40"
            >
              Previous
            </button>

            <button
              type="button"
              disabled={offset + PAGE_SIZE >= data.total}
              onClick={() => {
                setOffset(offset + PAGE_SIZE);
              }}
              className="rounded border px-3 py-2 disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </>
      )}
    </section>
  );
}