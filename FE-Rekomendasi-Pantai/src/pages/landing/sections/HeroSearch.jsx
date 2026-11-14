import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { Search, ArrowUpRight } from "lucide-react";
import { useAuth } from "../../../context/AuthContext";

const CONTOH_PENCARIAN = [
  "Pasir putih dan Sepi Pengunjung",
  "Parkir luas,ada toilet, dan ada warung",
  "Snorkeling",
  "Cocok untuk keluarga",
];

export default function HeroSearch({ atribut = [] }) {
  const [query, setQuery] = useState("");

  const navigate = useNavigate();
  const location = useLocation();
  const { user, loading } = useAuth();

  function cari(teks) {
    const q = teks.trim();

    if (!q || loading) return;

    // Jika belum login, simpan query lalu arahkan ke Login.
    if (!user) {
      navigate("/login", {
        state: {
          from: "/",
          query: q,
        },
      });

      return;
    }

    // Hanya role user yang boleh mencari rekomendasi.
    if (user.role !== "user") {
      return;
    }

    // Pengguna sudah login sebagai user.
    navigate(`/hasil?q=${encodeURIComponent(q)}`);
  }

  function tambahAtribut(kata) {
    setQuery((sebelumnya) => {
      const kataSekarang = sebelumnya
        .split(",")
        .map((item) => item.trim().toLowerCase());

      if (kataSekarang.includes(kata.toLowerCase())) {
        return sebelumnya;
      }

      return sebelumnya.trim() ? `${sebelumnya.trim()}, ${kata}` : kata;
    });
  }

  return (
    <section className="relative bg-[#f8fafc] px-5 pb-24 pt-24 sm:pb-32 sm:pt-32">
      <div className="pointer-events-none absolute right-0 top-0 h-96 w-96 max-w-full rounded-full bg-sky-100/60 blur-3xl" />

      <div className="relative mx-auto max-w-4xl">
        <div className="mx-auto max-w-3xl text-center">
          <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl md:text-6xl">
            Pantai yang cocok
            <br className="hidden sm:block" /> untuk{" "}
            <span className="text-sky-600">caramu berlibur.</span>
          </h1>

          <p className="mx-auto mt-6 max-w-2xl text-base leading-7 text-slate-600 sm:text-lg">
            Punya pantai impian? Ceritakan apa yang kamu cari. Temukan
            rekomendasi berdasarkan karakteristik pantai dan ulasan pengunjung.
          </p>

          <form
            role="search"
            onSubmit={(e) => {
              e.preventDefault();
              cari(query);
            }}
            className="mx-auto mt-9 flex max-w-2xl items-center gap-2 rounded-2xl border border-slate-200 bg-white p-2 shadow-sm transition focus-within:border-sky-400 focus-within:ring-4 focus-within:ring-sky-100"
          >
            <Search
              className="ml-3 h-5 w-5 shrink-0 text-slate-400"
              aria-hidden="true"
            />

            <input
              type="text"
              value={query}
              maxLength={200}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Contoh: pasir putih, ombak tenang..."
              aria-label="Preferensi pantai"
              className="min-w-0 flex-1 bg-transparent px-2 py-3 text-sm text-slate-800 outline-none placeholder:text-slate-400 sm:text-base"
            />

            <button
              type="submit"
              disabled={!query.trim() || loading}
              className="inline-flex shrink-0 items-center gap-2 rounded-xl bg-sky-600 px-4 py-3 text-sm font-medium text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:opacity-40 sm:px-5"
            >
              {loading ? "Memeriksa..." : "Cari"}
              <ArrowUpRight className="h-4 w-4" />
            </button>
          </form>

          <div className="mx-auto mt-5 max-w-2xl text-left">
            <p className="mb-3 text-xs font-medium uppercase tracking-wider text-slate-500">
              Ide preferensi
            </p>

            <div className="flex flex-wrap gap-2">
              {CONTOH_PENCARIAN.map((contoh) => (
                <button
                  key={contoh}
                  type="button"
                  onClick={() => tambahAtribut(contoh)}
                  className="rounded-full border border-slate-200 bg-white px-3.5 py-2 text-sm text-slate-600 transition hover:border-sky-300 hover:bg-sky-50 hover:text-sky-700"
                >
                  + {contoh}
                </button>
              ))}

              {atribut.map((kata) => (
                <button
                  key={kata}
                  type="button"
                  onClick={() => tambahAtribut(kata)}
                  className="rounded-full border border-slate-200 bg-white px-3.5 py-2 text-sm text-slate-600 transition hover:border-sky-300 hover:bg-sky-50 hover:text-sky-700"
                >
                  + {kata}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
