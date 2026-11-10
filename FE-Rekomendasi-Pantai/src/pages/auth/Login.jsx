import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Waves, ArrowRight, UserRound, LockKeyhole } from "lucide-react";
import { useAuth } from "../../context/AuthContext";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setSubmitting(true);

    try {
      const data = await login(username.trim(), password);

      const destination = location.state?.from;
      const savedQuery = location.state?.query;

      if (data.user?.role === "admin") {
        navigate("/admin", { replace: true });
      } else if (savedQuery) {
        navigate(`/hasil?q=${encodeURIComponent(savedQuery)}`, {
          replace: true,
        });
      } else if (
        typeof destination === "string" &&
        destination !== "/login" &&
        destination !== "/register"
      ) {
        navigate(destination, { replace: true });
      } else if (
        destination?.pathname &&
        destination.pathname !== "/login" &&
        destination.pathname !== "/register"
      ) {
        navigate(destination.pathname, { replace: true });
      } else {
        navigate("/", { replace: true });
      }
    } catch (err) {
      setError(err.message || "Login gagal. Periksa username dan password.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-[#f8fafc] px-4 py-10">
      {/* Dekorasi latar */}
      <div className="pointer-events-none absolute -left-32 -top-32 h-96 w-96 rounded-full bg-sky-100/70 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-32 -right-32 h-96 w-96 rounded-full bg-blue-100/60 blur-3xl" />

      <div className="relative w-full max-w-md">
        <Link
          to="/"
          className="mb-8 flex items-center justify-center gap-2 text-slate-800 transition hover:text-sky-600"
        ></Link>

        <form
          onSubmit={handleSubmit}
          className="space-y-5 rounded-3xl border border-slate-200/80 bg-white/95 p-6 shadow-xl shadow-slate-200/50 backdrop-blur sm:p-8"
        >
          <div className="text-center">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900">
              Masuk ke akunmu
            </h1>

            <p className="mt-3 text-sm leading-6 text-slate-500">
              Login untuk menemukan pantai yang sesuai dengan caramu berlibur.
            </p>
          </div>

          {location.state?.registered && (
            <div
              role="status"
              className="rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-700"
            >
              Registrasi berhasil. Silakan login menggunakan akunmu.
            </div>
          )}

          {error && (
            <div
              role="alert"
              className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700"
            >
              {error}
            </div>
          )}

          <div className="space-y-2">
            <label
              htmlFor="username"
              className="block text-sm font-medium text-slate-700"
            >
              Username
            </label>

            <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-3 transition focus-within:border-sky-400 focus-within:ring-4 focus-within:ring-sky-100">
              <UserRound size={18} className="shrink-0 text-slate-400" />

              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                autoComplete="username"
                required
                placeholder="Masukkan username"
                className="min-w-0 flex-1 bg-transparent py-3 text-sm text-slate-800 outline-none placeholder:text-slate-400"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label
              htmlFor="password"
              className="block text-sm font-medium text-slate-700"
            >
              Password
            </label>

            <div className="flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-3 transition focus-within:border-sky-400 focus-within:ring-4 focus-within:ring-sky-100">
              <LockKeyhole size={18} className="shrink-0 text-slate-400" />

              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
                required
                placeholder="Masukkan password"
                className="min-w-0 flex-1 bg-transparent py-3 text-sm text-slate-800 outline-none placeholder:text-slate-400"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-sky-600 px-4 py-3.5 font-semibold text-white shadow-lg shadow-sky-600/20 transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {submitting ? "Memproses..." : "Login"}
            {!submitting && <ArrowRight size={18} />}
          </button>

          <p className="text-center text-sm text-slate-500">
            Belum punya akun?{" "}
            <Link
              to="/register"
              state={location.state}
              className="font-semibold text-sky-700 hover:text-sky-800 hover:underline"
            >
              Daftar sekarang
            </Link>
          </p>
        </form>

        <p className="mt-6 text-center text-xs text-slate-400">
          Jelajahi keindahan pantai Malang Selatan.
        </p>
      </div>
    </main>
  );
}
