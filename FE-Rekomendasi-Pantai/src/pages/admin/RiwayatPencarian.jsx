import { useCallback, useEffect, useState } from "react";
import { RefreshCw, Search, AlertCircle } from "lucide-react";
import { ambilSemuaRiwayatPencarian } from "../../api/searchHistory";

export default function RiwayatPencarian() {
  const [riwayat, setRiwayat] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [keyword, setKeyword] = useState("");

  const fetchRiwayat = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const data = await ambilSemuaRiwayatPencarian();
      setRiwayat(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || "Gagal mengambil data riwayat.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchRiwayat();
  }, [fetchRiwayat]);

  const filteredRiwayat = riwayat.filter((item) =>
    (item.keyword || "").toLowerCase().includes(keyword.toLowerCase()),
  );

  const formatTanggal = (tanggal) => {
    if (!tanggal) return "-";

    const date = new Date(tanggal);

    if (Number.isNaN(date.getTime())) return "-";

    return new Intl.DateTimeFormat("id-ID", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(date);
  };

  return (
    <section className="space-y-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Riwayat Pencarian
          </h1>
          <p className="mt-2 text-sm text-slate-500">
            Pantau aktivitas pencarian pantai oleh pengguna.
          </p>
        </div>

        <button
          type="button"
          onClick={fetchRiwayat}
          disabled={loading}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-sky-600 px-4 py-3 text-sm font-semibold text-white hover:bg-sky-700 disabled:opacity-60"
        >
          <RefreshCw size={16} />
          Muat Ulang
        </button>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="relative max-w-md">
          <Search
            size={18}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
          />
          <input
            type="text"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="Cari berdasarkan kata kunci..."
            className="w-full rounded-xl border border-slate-200 py-3 pl-10 pr-4 text-sm outline-none focus:border-sky-400 focus:ring-4 focus:ring-sky-100"
          />
        </div>
      </div>

      {error && (
        <div
          role="alert"
          className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"
        >
          <AlertCircle size={18} className="mt-0.5 shrink-0" />
          <div>
            <p className="font-semibold">Gagal memuat riwayat</p>
            <p className="mt-1">{error}</p>
          </div>
        </div>
      )}

      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="flex items-center justify-between border-b border-slate-100 p-5">
          <div>
            <h2 className="font-bold text-slate-900">Data Pencarian</h2>
            <p className="mt-1 text-xs text-slate-500">
              {filteredRiwayat.length} data ditampilkan
            </p>
          </div>
        </div>

        {loading ? (
          <div className="p-10 text-center text-sm text-slate-500">
            Memuat riwayat pencarian...
          </div>
        ) : !error && filteredRiwayat.length === 0 ? (
          <div className="p-10 text-center text-sm text-slate-500">
            Belum ada riwayat pencarian yang cocok.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[700px] text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-5 py-4">Waktu</th>
                  <th className="px-5 py-4">ID Pengguna</th>
                  <th className="px-5 py-4">Kata Kunci</th>
                  <th className="px-5 py-4 text-center">Jumlah Hasil</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-100">
                {filteredRiwayat.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50">
                    <td className="whitespace-nowrap px-5 py-4 text-slate-500">
                      {formatTanggal(item.created_at)}
                    </td>
                    <td className="px-5 py-4 text-slate-600">
                      {item.user_id ?? "-"}
                    </td>
                    <td className="px-5 py-4 font-medium text-slate-800">
                      {item.keyword}
                    </td>
                    <td className="px-5 py-4 text-center">
                      <span className="rounded-full bg-sky-50 px-3 py-1 font-semibold text-sky-700">
                        {item.result_count ?? 0}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}
