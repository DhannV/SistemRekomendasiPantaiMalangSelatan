import { useEffect, useState } from "react";
import { TrendingUp, RefreshCw } from "lucide-react";
import { ambilKataKunciPopuler } from "../../api/searchHistory";

export default function KataKunciPopuler() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function fetchData() {
    setLoading(true);
    setError("");

    try {
      const hasil = await ambilKataKunciPopuler();
      setData(Array.isArray(hasil) ? hasil : []);
    } catch (err) {
      setError(err.message || "Gagal mengambil kata kunci populer.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <section className="space-y-6">
      <div className="flex items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Kata Kunci Populer
          </h1>
          <p className="mt-2 text-sm text-slate-500">
            Kata kunci yang paling sering dicari pengguna.
          </p>
        </div>

        <button
          onClick={fetchData}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-xl bg-sky-600 px-4 py-3 text-sm font-semibold text-white hover:bg-sky-700 disabled:opacity-60"
        >
          <RefreshCw size={16} />
          Muat Ulang
        </button>
      </div>

      {error && (
        <p
          role="alert"
          className="rounded-xl bg-red-50 p-4 text-sm text-red-700"
        >
          {error}
        </p>
      )}

      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        {loading ? (
          <p className="p-8 text-center text-sm text-slate-500">
            Memuat kata kunci...
          </p>
        ) : !error && data.length === 0 ? (
          <p className="p-8 text-center text-sm text-slate-500">
            Belum ada data pencarian.
          </p>
        ) : (
          <div className="divide-y divide-slate-100">
            {data.map((item, index) => (
              <div key={item.keyword} className="flex items-center gap-4 p-5">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-sky-50 text-sky-700">
                  {index + 1}
                </div>

                <div className="min-w-0 flex-1">
                  <p className="break-words font-semibold text-slate-800">
                    {item.keyword}
                  </p>
                  <p className="mt-1 text-xs text-slate-500">Total pencarian</p>
                </div>

                <div className="flex items-center gap-2 font-bold text-sky-700">
                  <TrendingUp size={17} />
                  {item.total_search}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
