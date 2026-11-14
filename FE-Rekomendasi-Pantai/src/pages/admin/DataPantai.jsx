import { useEffect, useState } from "react";
import {
  Search,
  RefreshCw,
  MapPin,
  Star,
  AlertCircle,
  MessageSquare,
  Users,
  Plus,
  Trash2,
  X,
} from "lucide-react";

import { apiRequest } from "../../api/auth";

export default function DataPantai() {
  const [pantai, setPantai] = useState([]);
  const [jumlahDataAsli, setJumlahDataAsli] = useState(0);
  const [keyword, setKeyword] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // State modal
  const [modalTambah, setModalTambah] = useState(false);
  const [modalHapus, setModalHapus] = useState(false);

  // State tambah
  const [namaPantai, setNamaPantai] = useState("");
  const [menyimpan, setMenyimpan] = useState(false);

  // State hapus
  const [daftarPantaiAdmin, setDaftarPantaiAdmin] = useState([]);
  const [pantaiDipilih, setPantaiDipilih] = useState("");
  const [memuatDaftar, setMemuatDaftar] = useState(false);
  const [menghapus, setMenghapus] = useState(false);

  // Notifikasi
  const [actionError, setActionError] = useState("");
  const [success, setSuccess] = useState("");

  // Mengambil data pantai untuk tabel
  const fetchPantai = async () => {
    try {
      setLoading(true);
      setError("");

      const result = await apiRequest("/pantai");

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

  // Mengambil daftar pantai untuk modal hapus
  const fetchDaftarPantaiAdmin = async () => {
    try {
      setMemuatDaftar(true);
      setActionError("");

      const result = await apiRequest("/pantai/admin/daftar");

      const data = Array.isArray(result)
        ? result
        : Array.isArray(result.data)
          ? result.data
          : [];

      setDaftarPantaiAdmin(data);
    } catch (err) {
      setActionError(err.message || "Gagal mengambil daftar pantai.");
    } finally {
      setMemuatDaftar(false);
    }
  };

  useEffect(() => {
    fetchPantai();
  }, []);

  // Membuka modal tambah
  const bukaModalTambah = () => {
    setNamaPantai("");
    setActionError("");
    setSuccess("");
    setModalTambah(true);
  };

  // Membuka modal hapus
  const bukaModalHapus = () => {
    setPantaiDipilih("");
    setActionError("");
    setSuccess("");
    setModalHapus(true);
    fetchDaftarPantaiAdmin();
  };

  // Menambahkan pantai
  const handleTambah = async (event) => {
    event.preventDefault();

    const nama = namaPantai.trim();

    if (!nama) {
      setActionError("Nama pantai tidak boleh kosong.");
      return;
    }

    try {
      setMenyimpan(true);
      setActionError("");

      await apiRequest("/pantai/admin", {
        method: "POST",
        body: JSON.stringify({
          nama_pantai: nama,
        }),
      });

      setModalTambah(false);
      setNamaPantai("");
      setSuccess(`Pantai ${nama} berhasil ditambahkan.`);

      await fetchPantai();
    } catch (err) {
      setActionError(err.message || "Gagal menambahkan pantai.");
    } finally {
      setMenyimpan(false);
    }
  };

  // Menghapus pantai
  const handleHapus = async () => {
    if (!pantaiDipilih) {
      setActionError("Silakan pilih pantai yang ingin dihapus.");
      return;
    }

    const pantaiTerpilih = daftarPantaiAdmin.find(
      (item) => String(item.id) === String(pantaiDipilih),
    );

    if (!pantaiTerpilih) {
      setActionError("Data pantai tidak ditemukan.");
      return;
    }

    try {
      setMenghapus(true);
      setActionError("");

      await apiRequest(`/pantai/admin/${pantaiDipilih}`, {
        method: "DELETE",
      });

      setModalHapus(false);
      setPantaiDipilih("");

      setSuccess(`Pantai ${pantaiTerpilih.nama_pantai} berhasil dihapus.`);

      await fetchPantai();
    } catch (err) {
      setActionError(err.message || "Gagal menghapus pantai.");
    } finally {
      setMenghapus(false);
    }
  };

  // Pencarian
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

  // Statistik
  const totalUlasan = pantai.reduce(
    (total, item) => total + Number(item.jumlah_ulasan ?? 0),
    0,
  );

  const pantaiDenganRating = pantai.filter((item) => item.rating != null);

  const rataRataRating =
    pantaiDenganRating.length > 0
      ? (
          pantaiDenganRating.reduce(
            (total, item) => total + Number(item.rating),
            0,
          ) / pantaiDenganRating.length
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

      {/* Notifikasi sukses */}
      {success && (
        <div className="flex items-center justify-between gap-3 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700">
          <p>{success}</p>
          <button onClick={() => setSuccess("")}>
            <X size={18} />
          </button>
        </div>
      )}

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
        {/* Header tabel */}
        <div className="flex flex-col gap-4 border-b border-slate-100 p-5">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <h2 className="font-semibold text-slate-800">Daftar Pantai</h2>

              <p className="mt-1 text-sm text-slate-500">
                Setiap nama pantai ditampilkan satu kali.
              </p>
            </div>

            {/* Tombol tambah dan hapus */}
            <div className="flex flex-wrap gap-2">
              <button
                onClick={bukaModalTambah}
                className="flex items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-blue-700"
              >
                <Plus size={17} />
                Tambah Data
              </button>

              <button
                onClick={bukaModalHapus}
                className="flex items-center justify-center gap-2 rounded-xl bg-red-50 px-4 py-2.5 text-sm font-medium text-red-600 transition hover:bg-red-100"
              >
                <Trash2 size={17} />
                Hapus Data
              </button>
            </div>
          </div>

          {/* Pencarian dan refresh */}
          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1 sm:max-w-sm">
              <Search
                size={18}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
              />

              <input
                type="text"
                value={keyword}
                onChange={(e) => setKeyword(e.target.value)}
                placeholder="Cari nama atau ulasan..."
                className="w-full rounded-xl border border-slate-200 py-2.5 pl-10 pr-4 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
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
                    key={item.id ?? String(item.pantai).toLowerCase()}
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

      {/* Modal Tambah */}
      {modalTambah && (
        <Modal title="Tambah Pantai" onClose={() => setModalTambah(false)}>
          <form onSubmit={handleTambah} className="space-y-5">
            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Nama Pantai
              </label>

              <input
                type="text"
                value={namaPantai}
                onChange={(e) => setNamaPantai(e.target.value)}
                placeholder="Contoh: Pantai Balekambang"
                autoFocus
                required
                className="w-full rounded-xl border border-slate-200 px-4 py-3 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              />

              <p className="mt-2 text-xs text-slate-500">
                Nama pantai akan ditambahkan ke daftar pantai utama.
              </p>
            </div>

            {actionError && <ActionError message={actionError} />}

            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setModalTambah(false)}
                disabled={menyimpan}
                className="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-600 transition hover:bg-slate-50"
              >
                Batal
              </button>

              <button
                type="submit"
                disabled={menyimpan}
                className="flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-blue-700 disabled:opacity-60"
              >
                <Plus size={16} />
                {menyimpan ? "Menyimpan..." : "Simpan Pantai"}
              </button>
            </div>
          </form>
        </Modal>
      )}

      {/* Modal Hapus */}
      {modalHapus && (
        <Modal title="Hapus Pantai" onClose={() => setModalHapus(false)}>
          <div className="space-y-5">
            <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4">
              <AlertCircle
                size={20}
                className="mt-0.5 shrink-0 text-amber-600"
              />

              <p className="text-sm leading-6 text-amber-800">
                Pantai yang dihapus akan hilang dari daftar website,
                rekomendasi, dan peta. Data ulasan serta koordinat lama tetap
                disimpan.
              </p>
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium text-slate-700">
                Pilih Pantai
              </label>

              <select
                value={pantaiDipilih}
                onChange={(e) => setPantaiDipilih(e.target.value)}
                disabled={memuatDaftar || daftarPantaiAdmin.length === 0}
                className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none transition focus:border-red-400 focus:ring-2 focus:ring-red-100 disabled:bg-slate-50"
              >
                <option value="">
                  {memuatDaftar
                    ? "Memuat daftar pantai..."
                    : daftarPantaiAdmin.length === 0
                      ? "Tidak ada data pantai"
                      : "Pilih pantai yang akan dihapus"}
                </option>

                {daftarPantaiAdmin.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.nama_pantai}
                  </option>
                ))}
              </select>
            </div>

            {actionError && <ActionError message={actionError} />}

            <div className="flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setModalHapus(false)}
                disabled={menghapus}
                className="rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-medium text-slate-600 transition hover:bg-slate-50"
              >
                Batal
              </button>

              <button
                type="button"
                onClick={handleHapus}
                disabled={menghapus || memuatDaftar || !pantaiDipilih}
                className="flex items-center gap-2 rounded-xl bg-red-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-red-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <Trash2 size={16} />
                {menghapus ? "Menghapus..." : "Hapus Pantai"}
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}

// Komponen statistik
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

// Komponen modal
function Modal({ title, onClose, children }) {
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-slate-900/50 p-4 backdrop-blur-sm"
      onMouseDown={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div className="w-full max-w-md rounded-2xl bg-white p-5 shadow-2xl sm:p-6">
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-800">{title}</h2>

          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-2 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
          >
            <X size={20} />
          </button>
        </div>

        {children}
      </div>
    </div>
  );
}

// Komponen pesan error pada modal
function ActionError({ message }) {
  return (
    <div className="flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
      <AlertCircle size={18} className="mt-0.5 shrink-0" />
      <p>{message}</p>
    </div>
  );
}
