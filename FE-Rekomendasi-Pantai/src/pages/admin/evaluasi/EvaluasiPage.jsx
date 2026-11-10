import { useState } from "react";
import {
  Play,
  ClipboardCheck,
  Search,
  CheckCircle2,
  AlertCircle,
  BarChart3,
  LoaderCircle,
  Trophy,
  ChevronDown,
  Waves,
  Star,
} from "lucide-react";

const API_URL =
  import.meta.env.VITE_API_URL ||
  "https://sistemrekomendasipantaimalangselatan.onrender.com";

function formatNumber(value) {
  if (value === null || value === undefined) return "—";

  return Number(value).toLocaleString("id-ID", {
    minimumFractionDigits: 4,
    maximumFractionDigits: 4,
  });
}

function formatScore(value) {
  if (value === null || value === undefined) return "—";

  return Number(value).toLocaleString("id-ID", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 4,
  });
}

function getMethodName(item) {
  return (
    item?.nama_metode || item?.metode || item?.method || item?.nama || "Metode"
  );
}

function getResults(response) {
  return (
    response?.hasil_evaluasi ||
    response?.data?.hasil_evaluasi ||
    response?.data?.hasil ||
    []
  );
}

function getGroundTruthList(response) {
  if (Array.isArray(response)) return response;

  return (
    response?.ground_truth ||
    response?.data?.ground_truth ||
    response?.data ||
    []
  );
}

function StatCard({ title, value, description, icon: Icon, color }) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-medium text-slate-500">{title}</p>
          <p className="mt-3 text-3xl font-bold text-slate-900">
            {value ?? "—"}
          </p>
        </div>

        <div className={`rounded-xl p-3 ${color}`}>
          <Icon size={22} />
        </div>
      </div>

      <p className="mt-4 border-t border-slate-100 pt-3 text-xs text-slate-500">
        {description}
      </p>
    </div>
  );
}

function MetricBar({ label, value }) {
  const percentage = Math.max(0, Math.min(100, Number(value || 0) * 100));

  return (
    <div>
      <div className="mb-1 flex justify-between text-xs">
        <span className="font-medium text-slate-600">{label}</span>
        <span className="font-semibold text-slate-800">
          {formatNumber(value)}
        </span>
      </div>

      <div className="h-2 overflow-hidden rounded-full bg-slate-100">
        <div
          className="h-full rounded-full bg-sky-500 transition-all"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

export default function EvaluasiPage() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [groundTruth, setGroundTruth] = useState({});
  const [error, setError] = useState("");

  const runEvaluation = async () => {
    setLoading(true);
    setError("");
    setResult(null);
    setGroundTruth({});

    try {
      const token = sessionStorage.getItem("access_token");

      const headers = {
        Accept: "application/json",
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      };

      // 1. Jalankan evaluasi
      const response = await fetch(`${API_URL}/evaluasi/jalankan`, {
        method: "POST",
        headers,
      });

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            data?.message ||
            `Gagal menjalankan evaluasi. HTTP ${response.status}`,
        );
      }

      if (data?.status === "error") {
        throw new Error(data?.message || "Evaluasi gagal dijalankan.");
      }

      const methods = getResults(data);

      if (methods.length === 0) {
        throw new Error("Data hasil evaluasi tidak ditemukan.");
      }

      setResult(data);

      // 2. Ambil Ground Truth untuk setiap query yang berhasil
      const queryIds = [
        ...new Set(
          methods.flatMap((method) =>
            (method.detail || [])
              .filter((item) => item.query_id)
              .map((item) => item.query_id),
          ),
        ),
      ];

      const groundTruthData = {};

      await Promise.all(
        queryIds.map(async (queryId) => {
          try {
            const gtResponse = await fetch(
              `${API_URL}/evaluasi/ground-truth/${queryId}`,
              { headers },
            );

            if (!gtResponse.ok) return;

            const gtData = await gtResponse.json();
            const gtList = getGroundTruthList(gtData);

            groundTruthData[queryId] = Object.fromEntries(
              gtList.map((item) => [
                item.beach_name || item.pantai,
                Number(item.relevance),
              ]),
            );
          } catch (err) {
            console.error(
              `Gagal mengambil Ground Truth query ${queryId}:`,
              err,
            );
          }
        }),
      );

      setGroundTruth(groundTruthData);
    } catch (err) {
      console.error("Evaluasi gagal:", err);
      setError(err.message || "Terjadi kesalahan saat menjalankan evaluasi.");
    } finally {
      setLoading(false);
    }
  };

  const methods = getResults(result);

  const totalQueries = result?.jumlah_query_aktif ?? 0;
  const totalMethods = result?.jumlah_metode ?? methods.length;

  const validQueries =
    methods.length > 0 ? (methods[0]?.jumlah_query_valid ?? 0) : 0;

  const bestMethod =
    methods.length > 0
      ? [...methods].sort(
          (a, b) => Number(b.ndcg_at_5 || 0) - Number(a.ndcg_at_5 || 0),
        )[0]
      : null;

  const isSuccess = result?.status === "success";

  return (
    <div className="space-y-7">
      {/* Header */}
      <section>
        <div className="flex items-center gap-3">
          <div className="rounded-2xl bg-sky-100 p-3 text-sky-700">
            <ClipboardCheck size={25} />
          </div>

          <div>
            <h1 className="text-2xl font-bold text-slate-900">
              Evaluasi Sistem
            </h1>
            <p className="mt-1 text-sm text-slate-500">
              Evaluasi performa metode rekomendasi pantai Malang Selatan.
            </p>
          </div>
        </div>
      </section>

      {/* Informasi metode */}
      <section className="rounded-2xl border border-sky-100 bg-sky-50 p-5">
        <div className="flex items-start gap-3">
          <BarChart3 className="mt-0.5 shrink-0 text-sky-700" size={21} />

          <div>
            <h2 className="font-semibold text-sky-900">
              Pengukuran Performa Rekomendasi
            </h2>
            <p className="mt-1 text-sm leading-6 text-sky-800">
              Sistem membandingkan enam konfigurasi metode menggunakan
              Precision@5, Recall@5, dan NDCG@5. Perhitungan dilakukan
              berdasarkan Ground Truth yang telah dinilai.
            </p>
          </div>
        </div>
      </section>

      {/* Ringkasan */}
      <section>
        <div className="mb-4">
          <h2 className="font-bold text-slate-900">Ringkasan Evaluasi</h2>
          <p className="mt-1 text-sm text-slate-500">
            Informasi dari proses evaluasi terakhir.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          <StatCard
            title="Query Aktif"
            value={totalQueries}
            description="Jumlah query yang digunakan dalam evaluasi."
            icon={Search}
            color="bg-sky-50 text-sky-600"
          />

          <StatCard
            title="Query Valid"
            value={validQueries}
            description="Query yang berhasil dievaluasi."
            icon={CheckCircle2}
            color="bg-emerald-50 text-emerald-600"
          />

          <StatCard
            title="Metode Evaluasi"
            value={totalMethods}
            description="Jumlah konfigurasi metode yang dibandingkan."
            icon={BarChart3}
            color="bg-indigo-50 text-indigo-600"
          />
        </div>
      </section>

      {/* Tombol evaluasi */}
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <div className="flex flex-col justify-between gap-5 sm:flex-row sm:items-center">
          <div>
            <h2 className="font-bold text-slate-900">Jalankan Evaluasi</h2>
            <p className="mt-1 text-sm leading-6 text-slate-500">
              Jalankan perhitungan performa seluruh metode rekomendasi
              menggunakan Ground Truth yang tersedia.
            </p>
          </div>

          <button
            type="button"
            onClick={runEvaluation}
            disabled={loading}
            className="inline-flex shrink-0 items-center justify-center gap-2 rounded-xl bg-sky-600 px-5 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? (
              <>
                <LoaderCircle size={18} className="animate-spin" />
                Memproses...
              </>
            ) : (
              <>
                <Play size={18} />
                Jalankan Evaluasi
              </>
            )}
          </button>
        </div>

        {error && (
          <div
            role="alert"
            className="mt-5 flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700"
          >
            <AlertCircle size={19} className="mt-0.5 shrink-0" />
            <div>
              <p className="font-semibold">Evaluasi gagal dijalankan</p>
              <p className="mt-1">{error}</p>
            </div>
          </div>
        )}

        {isSuccess && (
          <div
            role="status"
            className="mt-5 flex items-start gap-3 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-sm text-emerald-700"
          >
            <CheckCircle2 size={19} className="mt-0.5 shrink-0" />
            <div>
              <p className="font-semibold">Evaluasi berhasil dijalankan</p>
              <p className="mt-1">
                Hasil perhitungan berhasil diterima dari backend.
              </p>
            </div>
          </div>
        )}
      </section>

      {result && methods.length > 0 && (
        <>
          {/* Metode terbaik */}
          {bestMethod && (
            <section className="rounded-2xl border border-amber-200 bg-amber-50 p-5 sm:p-6">
              <div className="flex items-start gap-3">
                <div className="rounded-xl bg-amber-100 p-3 text-amber-700">
                  <Trophy size={24} />
                </div>

                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-amber-800">
                    NDCG@5 Tertinggi
                  </p>

                  <h2 className="mt-1 text-xl font-bold text-amber-950">
                    {getMethodName(bestMethod)}
                  </h2>

                  <p className="mt-1 text-sm text-amber-800">
                    Memperoleh nilai NDCG@5 sebesar{" "}
                    <strong>{formatNumber(bestMethod.ndcg_at_5)}</strong>.
                  </p>
                </div>

                <Star size={23} className="shrink-0 text-amber-600" />
              </div>
            </section>
          )}

          {/* Tabel hasil evaluasi */}
          <section className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
            <div className="border-b border-slate-100 p-5">
              <h2 className="font-bold text-slate-900">
                Perbandingan Hasil Evaluasi
              </h2>
              <p className="mt-1 text-sm text-slate-500">
                Perbandingan nilai Precision@5, Recall@5, dan NDCG@5.
              </p>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full min-w-[720px] text-left text-sm">
                <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                  <tr>
                    <th className="px-5 py-4">Metode</th>
                    <th className="px-5 py-4 text-center">Query Valid</th>
                    <th className="px-5 py-4 text-center">Precision@5</th>
                    <th className="px-5 py-4 text-center">Recall@5</th>
                    <th className="px-5 py-4 text-center">NDCG@5</th>
                  </tr>
                </thead>

                <tbody className="divide-y divide-slate-100">
                  {methods.map((method, index) => {
                    const isBest =
                      bestMethod &&
                      getMethodName(method) === getMethodName(bestMethod);

                    return (
                      <tr
                        key={`${getMethodName(method)}-${index}`}
                        className="transition hover:bg-slate-50"
                      >
                        <td className="px-5 py-4 font-semibold text-slate-800">
                          <div className="flex items-center gap-2">
                            {getMethodName(method)}
                            {isBest && (
                              <span className="rounded-full bg-amber-100 px-2 py-1 text-[10px] font-semibold text-amber-700">
                                Terbaik
                              </span>
                            )}
                          </div>
                        </td>

                        <td className="px-5 py-4 text-center text-slate-600">
                          {method.jumlah_query_valid ?? 0}
                        </td>

                        <td className="px-5 py-4 text-center font-medium text-slate-700">
                          {formatNumber(method.precision_at_5)}
                        </td>

                        <td className="px-5 py-4 text-center font-medium text-slate-700">
                          {formatNumber(method.recall_at_5)}
                        </td>

                        <td className="px-5 py-4 text-center font-semibold text-slate-800">
                          {formatNumber(method.ndcg_at_5)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </section>

          {/* Visualisasi metrik */}
          <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
            <div className="mb-5">
              <h2 className="font-bold text-slate-900">Visualisasi NDCG@5</h2>
              <p className="mt-1 text-sm text-slate-500">
                Perbandingan kualitas urutan rekomendasi setiap metode.
              </p>
            </div>

            <div className="space-y-5">
              {methods.map((method, index) => (
                <div key={index}>
                  <p className="mb-2 text-sm font-medium text-slate-700">
                    {getMethodName(method)}
                  </p>
                  <MetricBar label="NDCG@5" value={method.ndcg_at_5} />
                </div>
              ))}
            </div>
          </section>

          {/* Detail rekomendasi */}
          <section>
            <div className="mb-4">
              <h2 className="font-bold text-slate-900">Detail Rekomendasi</h2>
              <p className="mt-1 text-sm text-slate-500">
                Lima pantai yang dihasilkan oleh setiap konfigurasi metode.
              </p>
            </div>

            <div className="space-y-4">
              {methods.map((method, index) => {
                const detail = method.detail || [];

                return (
                  <details
                    key={index}
                    className="group overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"
                  >
                    <summary className="flex cursor-pointer list-none items-center justify-between gap-3 p-5">
                      <div className="min-w-0">
                        <h3 className="font-semibold text-slate-900">
                          {getMethodName(method)}
                        </h3>
                        <p className="mt-1 text-xs text-slate-500">
                          Precision {formatNumber(method.precision_at_5)}
                          {" · "}
                          Recall {formatNumber(method.recall_at_5)}
                          {" · "}
                          NDCG {formatNumber(method.ndcg_at_5)}
                        </p>
                      </div>

                      <ChevronDown
                        size={20}
                        className="shrink-0 text-slate-400 transition group-open:rotate-180"
                      />
                    </summary>

                    <div className="border-t border-slate-100 p-5">
                      {detail.map((queryDetail, detailIndex) => {
                        const queryId = queryDetail.query_id;
                        const gtMap = groundTruth[queryId] || {};
                        const recommendations = queryDetail.rekomendasi || [];

                        return (
                          <div key={detailIndex}>
                            <div className="mb-4 flex items-center gap-2">
                              <Waves size={17} className="text-sky-600" />
                              <p className="text-sm font-semibold text-slate-800">
                                Preferensi: {queryDetail.query}
                              </p>
                              <span className="rounded-full bg-emerald-50 px-2 py-1 text-xs font-medium text-emerald-700">
                                {queryDetail.status}
                              </span>
                            </div>

                            <div className="overflow-x-auto">
                              <table className="w-full min-w-[650px] text-left text-sm">
                                <thead className="bg-slate-50 text-xs text-slate-500">
                                  <tr>
                                    <th className="px-3 py-3">Peringkat</th>
                                    <th className="px-3 py-3">Nama Pantai</th>
                                    <th className="px-3 py-3 text-center">
                                      Ground Truth
                                    </th>
                                    <th className="px-3 py-3 text-center">
                                      Cosine
                                    </th>
                                    <th className="px-3 py-3 text-center">
                                      BWR
                                    </th>
                                    <th className="px-3 py-3 text-center">
                                      Skor Akhir
                                    </th>
                                  </tr>
                                </thead>

                                <tbody className="divide-y divide-slate-100">
                                  {recommendations.map(
                                    (item, recommendationIndex) => {
                                      const relevance = gtMap[item.pantai];

                                      return (
                                        <tr
                                          key={recommendationIndex}
                                          className="hover:bg-slate-50"
                                        >
                                          <td className="px-3 py-3 font-semibold text-slate-600">
                                            #{recommendationIndex + 1}
                                          </td>

                                          <td className="px-3 py-3 font-medium text-slate-800">
                                            {item.pantai}
                                          </td>

                                          <td className="px-3 py-3 text-center">
                                            {relevance !== undefined ? (
                                              <span
                                                className={`rounded-full px-2.5 py-1 text-xs font-semibold ${
                                                  relevance === 0
                                                    ? "bg-red-50 text-red-600"
                                                    : relevance === 1
                                                      ? "bg-slate-100 text-slate-700"
                                                      : relevance === 2
                                                        ? "bg-sky-50 text-sky-700"
                                                        : "bg-emerald-50 text-emerald-700"
                                                }`}
                                              >
                                                {relevance}
                                              </span>
                                            ) : (
                                              <span className="text-slate-400">
                                                —
                                              </span>
                                            )}
                                          </td>

                                          <td className="px-3 py-3 text-center text-slate-600">
                                            {formatScore(item.skor_cosine)}
                                          </td>

                                          <td className="px-3 py-3 text-center text-slate-600">
                                            {formatScore(item.skor_bwr)}
                                          </td>

                                          <td className="px-3 py-3 text-center font-semibold text-sky-700">
                                            {formatScore(item.skor_akhir)}
                                          </td>
                                        </tr>
                                      );
                                    },
                                  )}
                                </tbody>
                              </table>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </details>
                );
              })}
            </div>
          </section>
        </>
      )}
    </div>
  );
}
