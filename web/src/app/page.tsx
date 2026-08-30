import PersistedAssets from "@/components/persisted-assets";
import ProductionDashboard from "@/components/production-dashboard";
import ApiHealth from "@/components/api-health";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-50 px-6 py-12 text-slate-950">
      <div className="mx-auto grid max-w-3xl gap-8">
        <header className="grid gap-3">
          <p className="text-sm font-semibold uppercase tracking-widest text-blue-700">
            Production monitoring MVP
          </p>

          <h1 className="text-4xl font-bold tracking-tight">
            Asset prediction dashboard
          </h1>

          <p className="max-w-2xl text-slate-600">
            Create an asset, submit its readings, and receive a
            deterministic prediction from the FastAPI backend.
          </p>
        </header>
        <ApiHealth />
        <ProductionDashboard />
        <PersistedAssets />
      </div>
    </main>
  );
}