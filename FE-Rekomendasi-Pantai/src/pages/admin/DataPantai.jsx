import { useEffect, useState } from "react";
import {
  Search,
  RefreshCw,
  MapPin,
  Star,
  AlertCircle,
  MessageSquare,
  Users,
} from "lucide-react";

const API_URL = "https://sistemrekomendasipantaimalangselatan.onrender.com";

export default function DataPantai() {
  const [pantai, setPantai] = useState([]);
  const [jumlahDataAsli, setJumlahDataAsli] = useState(0);
  const [keyword, setKeyword] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchPantai = async () => {
    try {
      setLoading(true);
      setError("");

      const response = await fetch(`${API_URL}/pantai`);

      if (!response.ok) {
        throw new Error("Gagal mengambil data pantai dari server.");
      }

      const result = await response.json();

      const daftarPantai = Array.isArray(result)
        ? result
        : Array.isArray(result.data)
          ? result.data
          : [];

      setPantai(daftarPantai);
      setJumlahDataAsli(Number(result.jumlah_data_asli ?? daftarPantai.length));
    } catch (err) {
      setError(
        err.message ||
          "Tidak dapat terhubung ke server. Pastikan FastAPI berjalan.",
      );
      setPantai([]);
      setJumlahDataAsli(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPantai();
  }, []);

  const pencarian = keyword.trim().toLocaleLowerCase("id-ID");

  const filteredPantai = pantai.filter((item) => {
    const nama = String(item.pantai ?? "").toLocaleLowerCase("id-ID");
    const deskripsi = String(item.teks ?? "").toLocaleLowerCase("id-ID");
    const users = String(item.user ?? "").toLocaleLowerCase("id-ID");

    return (
      nama.includes(pencarian) ||
      deskripsi.includes(pencarian) ||
      users.includes(pencarian)
    );
  });

  const totalUlasan = pantai.reduce(
    (total, item) => total + Number(item.jumlah_ulasan ?? 0),
    0,
  );

  const rataRataRating =
    pantai.filter((item) => item.rating != null).length > 0
      ? (
          pantai.reduce(
            (total, item) =>
              total + (item.rating == null ? 0 : Number(item.rating)),
            0,
          ) / pantai.filter((item) => item.rating != null).length
        ).toFixed(2)
      : "-";

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <p className="text-sm font-medium text-blue-600">Manajemen Data</p>

        <h1 className="mt-1 text-2xl font-bold text-slate-800 md:text-3xl">
          Data Pantai
        </h1>

        <p className="mt-2 text-sm text-slate-500">
          Kelola dan cari data pantai yang digunakan dalam sistem rekomendasi.
        </p>
      </div>

      {/* Statistik */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Total Pantai Unik"
          value={loading ? "..." : pantai.length}
          icon={<MapPin size={24} />}
          color="blue"
        />

        <StatCard
          label="Total Baris Dataset"
          value={loading ? "..." : jumlahDataAsli}
          icon={<Users size={24} />}
          color="violet"
        />

        <StatCard
          label="Total Data Ulasan"
          value={loading ? "..." : totalUlasan}
          icon={<MessageSquare size={24} />}
          color="emerald"
        />

        <StatCard
          label="Rata-rata Rating Pantai"
          value={loading ? "..." : rataRataRating}
          icon={<Star size={24} />}
          color="amber"
        />
      </div>

      {/* Tabel */}
      <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="flex flex-col gap-4 border-b border-slate-100 p-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="font-semibold text-slate-800">Daftar Pantai</h2>

            <p className="mt-1 text-sm text-slate-500">
              Setiap nama pantai ditampilkan satu kali.
            </p>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative">
              <Search
                size={18}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
              />

              <input
                type="text"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                placeholder="Cari nama atau ulasan..."
                className="w-full rounded-xl border border-slate-200 py-2.5 pl-10 pr-4 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 sm:w-64"
              />
            </div>

            <button
              onClick={fetchPantai}
              disabled={loading}
              className="flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
            >
              <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
              Refresh
            </button>
          </div>
        </div>

        {/* Pesan error */}
        {error && (
          <div className="m-5 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            <AlertCircle size={20} className="mt-0.5 shrink-0" />

            <div>
              <p className="font-semibold">Gagal memuat data</p>
              <p className="mt-1">{error}</p>

              <button
                onClick={fetchPantai}
                className="mt-3 font-semibold underline"
              >
                Coba lagi
              </button>
            </div>
          </div>
        )}

        {/* Tabel responsif */}
        <div className="overflow-x-auto">
          <table className="w-full min-w-[850px] text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-5 py-4 font-semibold">No.</th>
                <th className="px-5 py-4 font-semibold">Nama Pantai</th>
                <th className="px-5 py-4 font-semibold">Rating Rata-rata</th>
                <th className="px-5 py-4 font-semibold">Jumlah Baris</th>
                <th className="px-5 py-4 font-semibold">User</th>
                <th className="px-5 py-4 font-semibold">Ulasan</th>
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-100">
              {loading ? (
                <tr>
                  <td
                    colSpan={6}
                    className="px-5 py-12 text-center text-slate-500"
                  >
                    Memuat data pantai...
                  </td>
                </tr>
              ) : error ? (
                <tr>
                  <td
                    colSpan={6}
                    className="px-5 py-12 text-center text-slate-500"
                  >
                    Data belum dapat ditampilkan.
                  </td>
                </tr>
              ) : filteredPantai.length === 0 ? (
                <tr>
                  <td
                    colSpan={6}
                    className="px-5 py-12 text-center text-slate-500"
                  >
                    Data pantai tidak ditemukan.
                  </td>
                </tr>
              ) : (
                filteredPantai.map((item, index) => (
                  <tr
                    key={String(item.pantai).toLocaleLowerCase("id-ID")}
                    className="transition hover:bg-slate-50"
                  >
                    <td className="px-5 py-4 text-slate-500">{index + 1}</td>

                    <td className="px-5 py-4 font-semibold text-slate-800">
                      {item.pantai || "-"}
                    </td>

                    <td className="px-5 py-4">
                      {item.rating != null ? (
                        <span className="inline-flex items-center gap-1 rounded-lg bg-amber-50 px-2.5 py-1 font-medium text-amber-700">
                          <Star size={14} fill="currentColor" />
                          {Number(item.rating).toFixed(2)}
                        </span>
                      ) : (
                        <span className="text-slate-400">Belum ada</span>
                      )}
                    </td>

                    <td className="px-5 py-4 text-slate-600">
                      {item.jumlah_ulasan ?? 0}
                    </td>

                    <td className="max-w-xs px-5 py-4 text-slate-600">
                      <p className="line-clamp-2">{item.user || "-"}</p>
                    </td>

                    <td className="max-w-md px-5 py-4 text-slate-600">
                      <p className="line-clamp-3 whitespace-normal">
                        {item.teks || "-"}
                      </p>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Footer */}
        <div className="flex flex-col gap-1 border-t border-slate-100 px-5 py-4 text-xs text-slate-500 sm:flex-row sm:items-center sm:justify-between">
          <span>
            Menampilkan {loading ? 0 : filteredPantai.length} dari{" "}
            {loading ? 0 : pantai.length} pantai unik
          </span>

          {!loading && !error && (
            <span>{jumlahDataAsli} baris dataset sebelum penggabungan</span>
          )}
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, icon, color }) {
  const colors = {
    blue: "bg-blue-50 text-blue-600",
    violet: "bg-violet-50 text-violet-600",
    emerald: "bg-emerald-50 text-emerald-600",
    amber: "bg-amber-50 text-amber-600",
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="text-sm text-slate-500">{label}</p>
          <p className="mt-2 text-3xl font-bold text-slate-800">{value}</p>
        </div>

        <div className={`rounded-xl p-3 ${colors[color]}`}>{icon}</div>
      </div>
    </div>
  );
}
