import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import DataPantai from "./DataPantai";
import RiwayatPencarian from "./RiwayatPencarian";
import KataKunciPopuler from "./KataKunciPopuler";
import KelolaAkun from "./KelolaAkun";
import EvaluasiPage from "./evaluasi/EvaluasiPage";

import {
  Waves,
  LayoutDashboard,
  History,
  TrendingUp,
  MapPin,
  Users,
  Menu,
  X,
  LogOut,
  Search,
  ChevronRight,
  Compass,
  ShieldCheck,
  ArrowUpRight,
  RefreshCw,
  CircleAlert,
  ClipboardCheck,
} from "lucide-react";

// Sesuaikan dengan URL backend di file .env frontend.
const API_URL =
  import.meta.env.VITE_API_URL ||
  "https://sistemrekomendasipantaimalangselatan.onrender.com";

// Sesuaikan path ini dengan route backend yang benar.
const API_PATHS = {
  users: "/users",
  history: "/search-history/admin",
  popular: "/search-history/admin/popular-keywords",
  pantai: "/pantai",
};

const menuItems = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "history", label: "Riwayat Pencarian", icon: History },
  { id: "popular", label: "Kata Kunci Populer", icon: TrendingUp },
  { id: "pantai", label: "Data Pantai", icon: MapPin },
  { id: "users", label: "Kelola Akun User", icon: Users },
  { id: "evaluasi", label: "Evaluasi Sistem", icon: ClipboardCheck },
];

const pageInfo = {
  history: {
    title: "Riwayat Pencarian",
    description: "Pantau aktivitas pencarian yang dilakukan pengguna.",
    icon: History,
  },
  popular: {
    title: "Kata Kunci Populer",
    description: "Temukan kata kunci yang paling sering dicari pengguna.",
    icon: TrendingUp,
  },
  users: {
    title: "Kelola Akun User",
    description: "Pantau akun pengguna yang terdaftar.",
    icon: Users,
  },
  evaluasi: {
    title: "Evaluasi Sistem",
    description:
      "Evaluasi performa metode rekomendasi pantai menggunakan Precision@5, Recall@5, dan NDCG@5.",
    icon: ClipboardCheck,
  },
};

const initialStats = {
  users: null,
  searches: null,
  popular: null,
  pantai: null,
};

function getArray(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.data)) return data.data;
  if (Array.isArray(data?.items)) return data.items;
  if (Array.isArray(data?.results)) return data.results;
  return null;
}

function StatCard({ title, value, description, icon: Icon, color }) {
  return (
    <div className="rounded-2xl border border-slate-200/80 bg-white p-5 shadow-sm transition duration-200 hover:-translate-y-1 hover:shadow-lg">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <p className="mt-3 break-words text-3xl font-bold tracking-tight text-slate-900">
            {value}
          </p>
        </div>

        <div className={`shrink-0 rounded-2xl p-3 ${color}`}>
          <Icon size={22} />
        </div>
      </div>

      <p className="mt-4 border-t border-slate-100 pt-3 text-xs leading-5 text-slate-500">
        {description}
      </p>
    </div>
  );
}

function ComingSoon({ page, onBack }) {
  const Icon = page?.icon || CircleAlert;

  return (
    <div className="flex min-h-[55vh] items-center justify-center">
      <div className="w-full max-w-lg rounded-3xl border border-slate-200 bg-white px-6 py-12 text-center shadow-sm sm:px-10">
        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-3xl bg-sky-50 text-sky-600">
          <Icon size={34} />
        </div>

        <h2 className="mt-6 text-2xl font-bold text-slate-900">
          {page?.title || "Halaman"}
        </h2>

        <p className="mx-auto mt-3 max-w-sm text-sm leading-6 text-slate-500">
          {page?.description}
        </p>

        <button
          type="button"
          onClick={onBack}
          className="mt-8 rounded-xl bg-sky-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-sky-700"
        >
          Kembali ke Dashboard
        </button>
      </div>
    </div>
  );
}

export default function AdminDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [activeMenu, setActiveMenu] = useState("dashboard");
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [stats, setStats] = useState(initialStats);
  const [loadingStats, setLoadingStats] = useState(false);
  const [statsError, setStatsError] = useState("");

  const activeItem = menuItems.find((item) => item.id === activeMenu);
  const username = user?.username || "Admin";
  const initials = username.slice(0, 2).toUpperCase();

  const fetchDashboardStats = useCallback(async () => {
    setLoadingStats(true);
    setStatsError("");

    const token = sessionStorage.getItem("access_token");

    const fetchEndpoint = async (path) => {
      const response = await fetch(`${API_URL}${path}`, {
        headers: {
          Accept: "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
      });

      if (!response.ok) {
        throw new Error(
          `${path}: HTTP ${response.status} ${response.statusText}`,
        );
      }

      return response.json();
    };

    // Setiap kartu diambil secara terpisah supaya kegagalan satu
    // endpoint tidak menghalangi kartu statistik lainnya.
    const tasks = [
      ["users", API_PATHS.users],
      ["searches", API_PATHS.history],
      ["popular", API_PATHS.popular],
      ["pantai", API_PATHS.pantai],
    ];

    const results = await Promise.all(
      tasks.map(async ([key, path]) => {
        try {
          const data = await fetchEndpoint(path);
          const rows = getArray(data);

          if (!rows) {
            throw new Error(
              `Respons ${path} bukan array. Periksa format JSON API.`,
            );
          }

          return { key, value: rows.length, error: null };
        } catch (error) {
          console.error(`Gagal mengambil statistik ${key}:`, error);
          return { key, value: null, error: `${key}: ${error.message}` };
        }
      }),
    );

    const nextStats = { ...initialStats };
    const errors = [];

    results.forEach(({ key, value, error }) => {
      nextStats[key] = value;
      if (error) errors.push(error);
    });

    setStats(nextStats);

    if (errors.length) {
      setStatsError(
        "Sebagian statistik belum berhasil dimuat. Periksa endpoint backend dan koneksi API.",
      );
    }

    setLoadingStats(false);
  }, []);

  useEffect(() => {
    fetchDashboardStats();
  }, [fetchDashboardStats]);

  const handleMenuChange = (id) => {
    setActiveMenu(id);
    setSidebarOpen(false);
  };

  const handleLogout = () => {
    logout();
    navigate("/login", { replace: true });
  };

  const formatStat = (value) => {
    if (loadingStats && value === null) return "Memuat...";
    if (value === null) return "—";
    return new Intl.NumberFormat("id-ID").format(value);
  };

  const renderContent = () => {
    if (activeMenu === "dashboard") {
      return (
        <>
          <section className="relative isolate overflow-hidden rounded-3xl bg-gradient-to-br from-sky-700 via-sky-600 to-blue-700 p-6 text-white shadow-xl shadow-sky-900/10 sm:p-9 lg:p-10">
            <div className="absolute -right-16 -top-20 -z-10 h-72 w-72 rounded-full border-[35px] border-white/5" />
            <div className="absolute -bottom-24 right-24 -z-10 h-64 w-64 rounded-full bg-cyan-300/10 blur-2xl" />

            <div className="relative max-w-2xl">
              <div className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1.5 text-xs font-medium text-sky-50">
                <ShieldCheck size={15} />
                Panel Administrator
              </div>

              <h1 className="mt-5 text-2xl font-bold leading-tight tracking-tight sm:text-4xl">
                Selamat datang, {username}!
              </h1>

              <p className="mt-4 max-w-xl text-sm leading-7 text-sky-100 sm:text-base">
                Kelola informasi pantai dan pantau aktivitas website rekomendasi
                wisata Pantai Malang Selatan melalui satu tempat.
              </p>

              <button
                type="button"
                onClick={() => handleMenuChange("pantai")}
                className="mt-7 inline-flex items-center gap-2 rounded-xl bg-white px-5 py-3 text-sm font-semibold text-sky-700 shadow-sm transition hover:bg-sky-50"
              >
                Jelajahi Data Pantai
                <ArrowUpRight size={17} />
              </button>
            </div>

            <Waves
              size={210}
              strokeWidth={0.8}
              className="absolute -bottom-8 -right-8 -z-10 hidden text-white/10 md:block"
            />
          </section>

          <section className="mt-8">
            <div className="mb-5 flex flex-wrap items-end justify-between gap-3">
              <div>
                <h2 className="text-lg font-bold text-slate-900">
                  Ringkasan Website
                </h2>
                <p className="mt-1 text-sm text-slate-500">
                  Gambaran umum data dan aktivitas.
                </p>
              </div>

              <button
                type="button"
                onClick={fetchDashboardStats}
                disabled={loadingStats}
                className="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3.5 py-2.5 text-sm font-semibold text-slate-600 transition hover:border-sky-200 hover:text-sky-700 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <RefreshCw
                  size={16}
                  className={loadingStats ? "animate-spin" : ""}
                />
                {loadingStats ? "Memuat..." : "Refresh"}
              </button>
            </div>

            {statsError && (
              <div
                role="status"
                className="mb-4 flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800"
              >
                <CircleAlert size={19} className="mt-0.5 shrink-0" />
                <div>
                  <p className="font-semibold">{statsError}</p>
                  <p className="mt-1 text-xs leading-5">
                    Angka yang gagal diambil akan ditampilkan sebagai tanda
                    pisah, bukan dianggap nol.
                  </p>
                </div>
              </div>
            )}

            <div className="grid gap-4 sm:grid-cols-2 2xl:grid-cols-4">
              <StatCard
                title="Total Pengguna"
                value={formatStat(stats.users)}
                description="Jumlah akun yang terdaftar"
                icon={Users}
                color="bg-sky-50 text-sky-600"
              />

              <StatCard
                title="Total Pencarian"
                value={formatStat(stats.searches)}
                description="Aktivitas pencarian pengguna"
                icon={Search}
                color="bg-indigo-50 text-indigo-600"
              />

              <StatCard
                title="Kata Kunci Populer"
                value={formatStat(stats.popular)}
                description="Jumlah kata kunci yang dikembalikan API"
                icon={TrendingUp}
                color="bg-amber-50 text-amber-600"
              />

              <StatCard
                title="Data Pantai"
                value={formatStat(stats.pantai)}
                description="Jumlah data pantai yang dikembalikan API"
                icon={MapPin}
                color="bg-emerald-50 text-emerald-600"
              />
            </div>
          </section>

          <section className="mt-9">
            <div className="mb-5">
              <h2 className="text-lg font-bold text-slate-900">Akses Cepat</h2>
              <p className="mt-1 text-sm text-slate-500">
                Pilih bagian website yang ingin kamu kelola.
              </p>
            </div>

            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {menuItems.slice(1).map((item) => {
                const Icon = item.icon;

                return (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => handleMenuChange(item.id)}
                    className="group flex items-center gap-4 rounded-2xl border border-slate-200 bg-white p-5 text-left transition hover:border-sky-200 hover:shadow-md"
                  >
                    <div className="shrink-0 rounded-xl bg-sky-50 p-3 text-sky-600 transition group-hover:bg-sky-600 group-hover:text-white">
                      <Icon size={21} />
                    </div>

                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-semibold text-slate-800">
                        {item.label}
                      </p>
                      <p className="mt-1 text-xs text-slate-500">
                        Buka halaman
                      </p>
                    </div>

                    <ChevronRight
                      size={17}
                      className="shrink-0 text-slate-400 transition group-hover:translate-x-1 group-hover:text-sky-600"
                    />
                  </button>
                );
              })}
            </div>
          </section>

          <footer className="mt-10 border-t border-slate-200 pt-5 text-xs text-slate-400">
            © {new Date().getFullYear()} Admin Dashboard
          </footer>
        </>
      );
    }

    if (activeMenu === "pantai") return <DataPantai />;
    if (activeMenu === "history") return <RiwayatPencarian />;
    if (activeMenu === "popular") return <KataKunciPopuler />;
    if (activeMenu === "users") return <KelolaAkun />;
    if (activeMenu === "evaluasi") {
      return <EvaluasiPage />;
    }
    return (
      <ComingSoon
        page={pageInfo[activeMenu]}
        onBack={() => handleMenuChange("dashboard")}
      />
    );
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      {sidebarOpen && (
        <button
          type="button"
          aria-label="Tutup sidebar"
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-40 bg-slate-950/40 backdrop-blur-[2px] lg:hidden"
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-50 flex w-[270px] flex-col border-r border-slate-200 bg-white transition-transform duration-300 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        } lg:translate-x-0`}
      >
        <div className="flex h-20 shrink-0 items-center justify-between border-b border-slate-100 px-5">
          <div className="flex items-center gap-3">
            <div>
              <h1 className="text-lg font-extrabold tracking-tight text-slate-900">
                Admin Workspace
              </h1>
            </div>
          </div>

          <button
            type="button"
            onClick={() => setSidebarOpen(false)}
            aria-label="Tutup sidebar"
            className="rounded-lg p-2 text-slate-500 hover:bg-slate-100 lg:hidden"
          >
            <X size={19} />
          </button>
        </div>

        <div className="px-4 pt-7">
          <p className="mb-3 px-3 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-400">
            Menu Utama
          </p>

          <nav className="space-y-1.5">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const active = activeMenu === item.id;

              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => handleMenuChange(item.id)}
                  aria-current={active ? "page" : undefined}
                  className={`relative flex w-full items-center gap-3 rounded-xl px-3.5 py-3 text-left text-sm font-medium transition ${
                    active
                      ? "bg-sky-600 text-white shadow-md shadow-sky-600/20"
                      : "text-slate-600 hover:bg-sky-50 hover:text-sky-700"
                  }`}
                >
                  <Icon size={19} />
                  <span className="flex-1">{item.label}</span>
                  {active && <ChevronRight size={16} />}
                </button>
              );
            })}
          </nav>
        </div>

        <div className="mt-auto p-4">
          <button
            type="button"
            onClick={handleLogout}
            className="mt-3 flex w-full items-center gap-3 rounded-xl px-3.5 py-3 text-sm font-medium text-red-600 transition hover:bg-red-50"
          >
            <LogOut size={19} />
            Keluar dari akun
          </button>
        </div>
      </aside>

      <div className="min-h-screen lg:pl-[270px]">
        <header className="sticky top-0 z-30 flex h-20 items-center justify-between border-b border-slate-200/80 bg-white/90 px-4 backdrop-blur-xl sm:px-6 lg:px-8">
          <div className="flex min-w-0 items-center gap-3">
            <button
              type="button"
              onClick={() => setSidebarOpen(true)}
              aria-label="Buka sidebar"
              className="rounded-xl border border-slate-200 p-2.5 text-slate-600 transition hover:bg-slate-50 lg:hidden"
            >
              <Menu size={20} />
            </button>

            <div className="min-w-0">
              <h2 className="mt-0.5 truncate text-lg font-bold text-slate-900 sm:text-xl">
                {activeItem?.label || "Dashboard"}
              </h2>
            </div>
          </div>

          <div className="flex shrink-0 items-center gap-3 sm:gap-4">
            <div className="hidden text-right sm:block">
              <p className="text-sm font-semibold text-slate-800">{username}</p>
              <p className="mt-0.5 text-xs text-slate-500">Administrator</p>
            </div>

            <div className="flex h-10 w-10 items-center justify-center rounded-full border border-sky-100 bg-sky-50 text-sm font-bold text-sky-700">
              {initials}
            </div>
          </div>
        </header>

        <main className="mx-auto max-w-[1800px] p-4 sm:p-6 lg:p-8 xl:p-9">
          {renderContent()}
        </main>
      </div>
    </div>
  );
}
