import { useCallback, useEffect, useMemo, useState } from "react";
import {
  Search,
  RefreshCw,
  Users,
  ShieldCheck,
  UserRound,
  Trash2,
  AlertCircle,
  LoaderCircle,
} from "lucide-react";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export default function KelolaAkun() {
  const [users, setUsers] = useState([]);
  const [keyword, setKeyword] = useState("");
  const [filterRole, setFilterRole] = useState("semua");
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState(null);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const getToken = () => sessionStorage.getItem("access_token");

  const request = async (path, options = {}) => {
    const token = getToken();

    if (!token) {
      throw new Error("Sesi login tidak ditemukan. Silakan login kembali.");
    }

    const response = await fetch(`${API_URL}${path}`, {
      ...options,
      headers: {
        Authorization: `Bearer ${token}`,
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...options.headers,
      },
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(
        typeof data.detail === "string"
          ? data.detail
          : "Permintaan gagal diproses.",
      );
    }

    return data;
  };

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const data = await request("/users");
      setUsers(Array.isArray(data) ? data : []);
    } catch (err) {
      setError(err.message || "Gagal mengambil data akun.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const filteredUsers = useMemo(() => {
    return users.filter((user) => {
      const matchesKeyword = (user.username || "")
        .toLowerCase()
        .includes(keyword.trim().toLowerCase());

      const matchesRole = filterRole === "semua" || user.role === filterRole;

      return matchesKeyword && matchesRole;
    });
  }, [users, keyword, filterRole]);

  const handleRoleChange = async (user) => {
    const newRole = user.role === "admin" ? "user" : "admin";

    const confirmed = window.confirm(
      `Ubah role ${user.username} menjadi ${newRole}?`,
    );

    if (!confirmed) return;

    setProcessingId(user.id);
    setError("");
    setSuccess("");

    try {
      await request(`/users/${user.id}/role`, {
        method: "PATCH",
        body: JSON.stringify({ role: newRole }),
      });

      setSuccess(`Role akun ${user.username} berhasil diperbarui.`);
      await fetchUsers();
    } catch (err) {
      setError(err.message || "Gagal mengubah role akun.");
    } finally {
      setProcessingId(null);
    }
  };

  const handleDelete = async (user) => {
    const confirmed = window.confirm(
      `Yakin ingin menghapus akun "${user.username}"? Tindakan ini tidak dapat dibatalkan.`,
    );

    if (!confirmed) return;

    setProcessingId(user.id);
    setError("");
    setSuccess("");

    try {
      await request(`/users/${user.id}`, {
        method: "DELETE",
      });

      setUsers((current) => current.filter((item) => item.id !== user.id));

      setSuccess(`Akun ${user.username} berhasil dihapus.`);
    } catch (err) {
      setError(err.message || "Gagal menghapus akun.");
    } finally {
      setProcessingId(null);
    }
  };

  const formatDate = (value) => {
    if (!value) return "-";

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) return "-";

    return new Intl.DateTimeFormat("id-ID", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(date);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <section className="rounded-3xl bg-gradient-to-br from-sky-700 via-sky-600 to-blue-700 p-6 text-white shadow-lg sm:p-8">
        <div className="flex items-center gap-3">
          <div className="rounded-2xl bg-white/15 p-3">
            <Users size={28} />
          </div>

          <div>
            <h1 className="text-2xl font-bold">Kelola Akun User</h1>
            <p className="mt-1 text-sm text-sky-100">
              Kelola akun dan hak akses pengguna.
            </p>
          </div>
        </div>
      </section>

      {/* Statistik */}
      <section className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-500">Total Akun</span>
            <Users className="text-sky-600" size={22} />
          </div>
          <p className="mt-3 text-3xl font-bold text-slate-900">
            {users.length}
          </p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-500">Pengguna</span>
            <UserRound className="text-emerald-600" size={22} />
          </div>
          <p className="mt-3 text-3xl font-bold text-slate-900">
            {users.filter((user) => user.role === "user").length}
          </p>
        </div>

        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-sm text-slate-500">Administrator</span>
            <ShieldCheck className="text-amber-600" size={22} />
          </div>
          <p className="mt-3 text-3xl font-bold text-slate-900">
            {users.filter((user) => user.role === "admin").length}
          </p>
        </div>
      </section>

      {/* Pesan */}
      {error && (
        <div
          role="alert"
          className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"
        >
          <AlertCircle size={20} className="shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div
          role="status"
          className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700"
        >
          {success}
        </div>
      )}

      {/* Tabel akun */}
      <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
        <div className="flex flex-col gap-4 border-b border-slate-100 p-5 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="font-bold text-slate-900">Daftar Akun</h2>
            <p className="mt-1 text-sm text-slate-500">
              Cari akun dan atur hak aksesnya.
            </p>
          </div>

          <button
            type="button"
            onClick={fetchUsers}
            disabled={loading}
            className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:opacity-50"
          >
            <RefreshCw size={16} className={loading ? "animate-spin" : ""} />
            Muat Ulang
          </button>
        </div>

        <div className="flex flex-col gap-3 p-5 sm:flex-row">
          <div className="relative flex-1">
            <Search
              size={18}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
            />
            <input
              type="text"
              value={keyword}
              onChange={(event) => setKeyword(event.target.value)}
              placeholder="Cari username..."
              className="w-full rounded-xl border border-slate-200 py-3 pl-10 pr-4 text-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
            />
          </div>

          <select
            value={filterRole}
            onChange={(event) => setFilterRole(event.target.value)}
            className="rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm outline-none focus:border-sky-500"
          >
            <option value="semua">Semua Role</option>
            <option value="user">User</option>
            <option value="admin">Admin</option>
          </select>
        </div>

        {loading ? (
          <div className="flex min-h-48 items-center justify-center gap-3 text-sm text-slate-500">
            <LoaderCircle className="animate-spin" size={22} />
            Memuat data akun...
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[700px] text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                <tr>
                  <th className="px-5 py-4">ID</th>
                  <th className="px-5 py-4">Username</th>
                  <th className="px-5 py-4">Role</th>
                  <th className="px-5 py-4">Tanggal Daftar</th>
                  <th className="px-5 py-4 text-right">Aksi</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-100">
                {filteredUsers.map((user) => (
                  <tr key={user.id} className="transition hover:bg-slate-50">
                    <td className="px-5 py-4 text-slate-500">#{user.id}</td>

                    <td className="px-5 py-4 font-semibold text-slate-800">
                      {user.username}
                    </td>

                    <td className="px-5 py-4">
                      <span
                        className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${
                          user.role === "admin"
                            ? "bg-sky-100 text-sky-700"
                            : "bg-emerald-100 text-emerald-700"
                        }`}
                      >
                        {user.role === "admin" ? "Admin" : "User"}
                      </span>
                    </td>

                    <td className="px-5 py-4 text-slate-500">
                      {formatDate(user.created_at)}
                    </td>

                    <td className="px-5 py-4">
                      <div className="flex justify-end gap-2">
                        <button
                          type="button"
                          disabled={processingId === user.id}
                          onClick={() => handleRoleChange(user)}
                          className="rounded-lg border border-sky-200 px-3 py-2 text-xs font-semibold text-sky-700 transition hover:bg-sky-50 disabled:opacity-50"
                        >
                          {processingId === user.id
                            ? "Memproses..."
                            : user.role === "admin"
                              ? "Jadikan User"
                              : "Jadikan Admin"}
                        </button>

                        <button
                          type="button"
                          disabled={processingId === user.id}
                          onClick={() => handleDelete(user)}
                          title="Hapus akun"
                          className="rounded-lg border border-red-200 p-2 text-red-600 transition hover:bg-red-50 disabled:opacity-50"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}

                {filteredUsers.length === 0 && (
                  <tr>
                    <td
                      colSpan={5}
                      className="px-5 py-12 text-center text-slate-500"
                    >
                      {users.length === 0
                        ? "Belum ada akun yang tersedia."
                        : "Tidak ada akun yang sesuai dengan pencarian."}
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}

        <div className="border-t border-slate-100 px-5 py-4 text-xs text-slate-500">
          Menampilkan {filteredUsers.length} dari {users.length} akun.
        </div>
      </section>
    </div>
  );
}
