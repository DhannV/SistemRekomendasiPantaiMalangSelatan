import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import {
  ArrowLeft,
  Search,
  MapPin,
  Navigation,
  RefreshCw,
  Waves,
  Database,
  ChevronRight,
  AlertCircle,
  CheckCircle2,
  LocateFixed,
  X,
} from "lucide-react";

import { ambilRekomendasi, ambilKoordinatPantai } from "../../api/rekomendasi";

import { simpanRiwayatPencarian } from "../../api/searchHistory";

export default function SearchResult() {
  const [searchParams, setSearchParams] = useSearchParams();

  const queryUrl = searchParams.get("q") || "";

  // State pencarian
  const [query, setQuery] = useState(queryUrl);
  const [hasil, setHasil] = useState([]);
  const [queryBersih, setQueryBersih] = useState("");
  const [peringatan, setPeringatan] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // State modal detail pantai
  const [pantaiTerpilih, setPantaiTerpilih] = useState(null);

  // State lokasi dan koordinat pantai
  const [koordinatPantai, setKoordinatPantai] = useState([]);
  const [lokasiPengguna, setLokasiPengguna] = useState(null);
  const [loadingKoordinat, setLoadingKoordinat] = useState(true);
  const [loadingLokasi, setLoadingLokasi] = useState(false);
  const [statusLokasi, setStatusLokasi] = useState("");
  const [errorKoordinat, setErrorKoordinat] = useState("");

  // Mengikuti perubahan query pada URL
  useEffect(() => {
    setQuery(queryUrl);
  }, [queryUrl]);

  // Mengambil koordinat pantai dari backend
  useEffect(() => {
    let aktif = true;

    async function ambilDataKoordinat() {
      setLoadingKoordinat(true);
      setErrorKoordinat("");

      try {
        const data = await ambilKoordinatPantai();

        if (!aktif) return;

        setKoordinatPantai(data);
      } catch (err) {
        if (!aktif) return;

        console.error("Gagal mengambil koordinat pantai:", err);

        setErrorKoordinat("Data koordinat pantai tidak dapat dimuat.");
      } finally {
        if (aktif) {
          setLoadingKoordinat(false);
        }
      }
    }

    ambilDataKoordinat();

    return () => {
      aktif = false;
    };
  }, []);

  // Mengambil rekomendasi berdasarkan query
  useEffect(() => {
    if (!queryUrl.trim()) {
      setHasil([]);
      setError("");
      setPeringatan("");
      setQueryBersih("");
      setPantaiTerpilih(null);
      return;
    }

    let aktif = true;

    async function cariPantai() {
      setLoading(true);
      setError("");
      setPeringatan("");
      setPantaiTerpilih(null);

      try {
        const response = await ambilRekomendasi(queryUrl, 5);

        if (!aktif) return;

        const dataHasil = response.data || [];

        setHasil(dataHasil);
        setQueryBersih(response.query_bersih || "");
        setPeringatan(response.peringatan || "");

        // Menyimpan riwayat pencarian
        try {
          await simpanRiwayatPencarian(queryUrl, dataHasil.length);
        } catch (err) {
          console.error("Gagal menyimpan riwayat pencarian:", err);
        }
      } catch (err) {
        if (!aktif) return;

        setHasil([]);

        setError(err.message || "Tidak dapat terhubung ke server rekomendasi.");
      } finally {
        if (aktif) {
          setLoading(false);
        }
      }
    }

    cariPantai();

    return () => {
      aktif = false;
    };
  }, [queryUrl]);

  // Menutup modal dengan tombol Escape
  useEffect(() => {
    if (!pantaiTerpilih) return;

    function handleEscape(e) {
      if (e.key === "Escape") {
        setPantaiTerpilih(null);
      }
    }

    window.addEventListener("keydown", handleEscape);

    return () => {
      window.removeEventListener("keydown", handleEscape);
    };
  }, [pantaiTerpilih]);

  // Fungsi menghitung jarak menggunakan Haversine
  function hitungJarak(lat1, lon1, lat2, lon2) {
    const R = 6371;

    const toRad = (derajat) => (derajat * Math.PI) / 180;

    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);

    const a =
      Math.sin(dLat / 2) ** 2 +
      Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    return R * c;
  }

  // Meminta lokasi pengguna melalui browser
  function aktifkanLokasi() {
    if (!navigator.geolocation) {
      setStatusLokasi("Browser kamu tidak mendukung fitur lokasi.");
      return;
    }

    setLoadingLokasi(true);
    setStatusLokasi("");

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLokasiPengguna({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });

        setStatusLokasi("Lokasi berhasil ditemukan.");
        setLoadingLokasi(false);
      },
      (error) => {
        let pesan = "Gagal mengambil lokasi pengguna.";

        if (error.code === 1) {
          pesan = "Izin lokasi ditolak. Aktifkan izin lokasi pada browser.";
        } else if (error.code === 2) {
          pesan = "Lokasi pengguna tidak dapat ditemukan.";
        } else if (error.code === 3) {
          pesan = "Waktu pengambilan lokasi habis. Silakan coba lagi.";
        }

        setStatusLokasi(pesan);
        setLoadingLokasi(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 15000,
        maximumAge: 60000,
      },
    );
  }

  // Mengubah query pencarian
  function cariLagi(e) {
    e.preventDefault();

    const q = query.trim();

    if (!q) return;

    setSearchParams({ q });
  }

  // Mencocokkan nama pantai dan menghitung jarak
  function dapatkanJarak(namaPantai) {
    if (!lokasiPengguna) return null;

    const data = koordinatPantai.find(
      (item) =>
        item.pantai?.trim().toLowerCase() === namaPantai?.trim().toLowerCase(),
    );

    if (!data || data.latitude == null || data.longitude == null) {
      return null;
    }

    return hitungJarak(
      lokasiPengguna.latitude,
      lokasiPengguna.longitude,
      Number(data.latitude),
      Number(data.longitude),
    );
  }

  // Format skor menjadi persentase
  function formatPersen(nilai) {
    const angka = Number(nilai) || 0;

    return `${(angka * 100).toFixed(2)}%`;
  }

  // Jarak pantai yang sedang dibuka di modal
  const jarakModal = pantaiTerpilih
    ? dapatkanJarak(pantaiTerpilih.pantai)
    : null;

  return (
    <main className="min-h-screen bg-[#F7F9FC] px-4 py-8 text-slate-800 sm:px-6 lg:py-12">
      <div className="mx-auto max-w-6xl">
        {/* Tombol kembali */}
        <Link
          to="/"
          className="group inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2.5 text-sm font-medium text-slate-600 shadow-sm transition duration-200 hover:border-sky-200 hover:text-sky-700 hover:shadow-md"
        >
          <ArrowLeft
            size={16}
            className="transition-transform group-hover:-translate-x-1"
          />
          Kembali ke beranda
        </Link>

        {/* Header halaman */}
        <header className="relative mt-8 overflow-hidden rounded-3xl border border-slate-200/80 bg-white px-6 py-8 shadow-sm sm:px-9 sm:py-10">
          <div className="pointer-events-none absolute -right-12 -top-16 h-48 w-48 rounded-full bg-sky-100/70 blur-3xl" />
          <div className="pointer-events-none absolute -bottom-20 left-1/3 h-40 w-40 rounded-full bg-blue-50 blur-3xl" />

          <div className="relative">
            <h1 className="mt-5 max-w-3xl text-3xl font-extrabold leading-tight tracking-tight text-slate-900 sm:text-4xl lg:text-5xl">
              Temukan pantai yang cocok untuk{" "}
              <span className="text-sky-600">caramu berlibur.</span>
            </h1>

            <p className="mt-4 max-w-2xl text-sm leading-7 text-slate-500 sm:text-base">
              Jelajahi rekomendasi pantai di Malang Selatan berdasarkan
              preferensi, karakteristik pantai, serta data ulasan dan rating
              pengunjung.
            </p>

            {/* Form pencarian */}
            <form
              onSubmit={cariLagi}
              className="mt-7 flex max-w-3xl items-center gap-2 rounded-2xl border border-slate-200 bg-white p-2 shadow-sm transition-all duration-200 focus-within:border-sky-400 focus-within:ring-4 focus-within:ring-sky-100"
            >
              <Search className="ml-2 h-5 w-5 shrink-0 text-slate-400" />

              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                maxLength={200}
                placeholder="Contoh: pasir putih, ombak tenang..."
                aria-label="Ubah preferensi pantai"
                className="min-w-0 flex-1 bg-transparent px-2 py-3 text-sm text-slate-700 outline-none placeholder:text-slate-400 sm:text-base"
              />

              <button
                type="submit"
                disabled={!query.trim() || loading}
                className="inline-flex shrink-0 items-center gap-2 rounded-xl bg-sky-600 px-4 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-sky-700 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-50 sm:px-5"
              >
                Cari
                <ChevronRight size={16} />
              </button>
            </form>

            {/* Kata kunci preprocessing */}
            {queryBersih && !loading && (
              <div className="mt-5 flex flex-wrap items-center gap-2 text-sm">
                <span className="text-slate-500">
                  Kata kunci setelah preprocessing:
                </span>

                <span className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 font-medium text-slate-700">
                  {queryBersih}
                </span>
              </div>
            )}
          </div>
        </header>

        {/* Status loading rekomendasi */}
        {loading && (
          <div className="mt-8 rounded-3xl border border-slate-200 bg-white px-6 py-16 text-center shadow-sm">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-sky-50">
              <RefreshCw className="h-7 w-7 animate-spin text-sky-600" />
            </div>

            <h2 className="mt-5 text-lg font-bold text-slate-900">
              Mencari pantai yang sesuai...
            </h2>

            <p className="mt-2 text-sm leading-6 text-slate-500">
              Sistem sedang menghitung skor rekomendasi untuk preferensimu.
            </p>
          </div>
        )}

        {/* Status error */}
        {!loading && error && (
          <div
            role="alert"
            className="mt-8 flex gap-4 rounded-2xl border border-red-200 bg-red-50 p-5 sm:p-6"
          >
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-white text-red-600">
              <AlertCircle size={22} />
            </div>

            <div>
              <h2 className="font-bold text-red-800">
                Rekomendasi gagal dimuat
              </h2>

              <p className="mt-1 text-sm leading-6 text-red-700">{error}</p>

              <p className="mt-2 text-xs leading-5 text-red-600">
                Pastikan backend FastAPI berjalan dan konfigurasi CORS sudah
                benar.
              </p>
            </div>
          </div>
        )}

        {/* Peringatan API */}
        {!loading && !error && peringatan && (
          <div className="mt-6 flex items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm leading-6 text-amber-800">
            <AlertCircle size={19} className="mt-0.5 shrink-0" />
            <p>{peringatan}</p>
          </div>
        )}

        {/* Hasil rekomendasi */}
        {!loading && !error && hasil.length > 0 && (
          <section className="mt-10">
            <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <div className="flex items-center gap-2 text-sm font-semibold text-sky-700">
                  HASIL PENCARIAN
                </div>

                <h2 className="mt-2 text-2xl font-extrabold tracking-tight text-slate-900 sm:text-3xl">
                  Pantai rekomendasi
                </h2>

                <p className="mt-2 text-sm text-slate-500">
                  Ditemukan{" "}
                  <span className="font-semibold text-slate-700">
                    {hasil.length} pantai
                  </span>{" "}
                  berdasarkan preferensimu.
                </p>
              </div>
            </div>

            {/* Kartu rekomendasi */}
            <div className="grid gap-5 sm:grid-cols-2">
              {hasil.map((pantai, index) => {
                const skorAkhir = Number(pantai.skor_akhir) || 0;

                const skorCosine = Number(pantai.skor_cosine) || 0;

                const skorBwr = Number(pantai.skor_bwr) || 0;

                const persen = Math.max(0, Math.min(100, skorAkhir * 100));

                return (
                  <article
                    key={pantai.pantai}
                    className="group relative overflow-hidden rounded-2xl border border-slate-200/80 bg-white shadow-sm transition-all duration-300 hover:-translate-y-1 hover:border-sky-200 hover:shadow-xl hover:shadow-sky-900/5"
                  >
                    <button
                      type="button"
                      onClick={() => setPantaiTerpilih(pantai)}
                      aria-label={`Lihat detail ${pantai.pantai}`}
                      className="w-full p-5 text-left focus:outline-none focus-visible:ring-4 focus-visible:ring-sky-200 sm:p-6"
                    >
                      {/* Aksen bagian atas */}
                      <div className="absolute inset-x-0 top-0 h-1 bg-gradient-to-r from-sky-400 via-sky-600 to-blue-500 opacity-70 transition-opacity group-hover:opacity-100" />

                      <div className="flex items-start justify-between gap-3">
                        <div className="flex min-w-0 items-start gap-3">
                          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border border-sky-100 bg-sky-50 text-sm font-extrabold text-sky-700 transition-colors group-hover:bg-sky-600 group-hover:text-white">
                            {String(index + 1).padStart(2, "0")}
                          </div>

                          <div className="min-w-0 pt-0.5">
                            <h3 className="break-words text-lg font-bold leading-snug text-slate-900 transition-colors group-hover:text-sky-700">
                              {pantai.pantai}
                            </h3>

                            <p className="mt-2 flex items-center gap-1.5 text-xs text-slate-500">
                              <MapPin
                                size={14}
                                className="shrink-0 text-sky-600"
                              />
                              Malang Selatan
                            </p>
                          </div>
                        </div>

                        {/* Skor akhir */}
                        <div className="shrink-0 rounded-xl bg-sky-50 px-3 py-2 text-right">
                          <p className="text-[10px] font-semibold uppercase tracking-wider text-sky-700">
                            Skor akhir
                          </p>

                          <p className="mt-0.5 text-xl font-extrabold tabular-nums text-sky-700">
                            {persen.toFixed(1)}%
                          </p>
                        </div>
                      </div>

                      {/* Ringkasan skor */}
                      <div className="mt-6 rounded-xl bg-slate-50 p-4">
                        <div className="flex items-center justify-between gap-3 text-sm">
                          <span className="text-slate-500">
                            Cosine Similarity
                          </span>

                          <span className="font-semibold tabular-nums text-slate-800">
                            {skorCosine.toFixed(4)}
                          </span>
                        </div>

                        <div className="mt-3 flex items-center justify-between gap-3 text-sm">
                          <span className="text-slate-500">
                            Bayesian Weighted Rating
                          </span>

                          <span className="font-semibold tabular-nums text-slate-800">
                            {skorBwr.toFixed(4)}
                          </span>
                        </div>

                        <div className="mt-4">
                          <div className="mb-2 flex items-center justify-between text-xs">
                            <span className="font-medium text-slate-500">
                              Skor gabungan
                            </span>

                            <span className="font-bold text-sky-700">
                              {persen.toFixed(1)}%
                            </span>
                          </div>

                          <div
                            className="h-2 overflow-hidden rounded-full bg-slate-200"
                            role="progressbar"
                            aria-label={`Skor akhir ${pantai.pantai}`}
                            aria-valuenow={Number(persen.toFixed(1))}
                            aria-valuemin={0}
                            aria-valuemax={100}
                          >
                            <div
                              className="h-full rounded-full bg-gradient-to-r from-sky-400 to-sky-600 transition-all duration-700"
                              style={{ width: `${persen}%` }}
                            />
                          </div>
                        </div>
                      </div>

                      {/* Keterangan klik */}
                      <div className="mt-4 flex items-center justify-between gap-3">
                        <div className="flex items-center gap-2 text-xs leading-5 text-slate-400">
                          <Database size={14} className="shrink-0" />
                          Detail rekomendasi hybrid
                        </div>

                        <span className="inline-flex items-center gap-1 text-xs font-semibold text-sky-700 transition group-hover:gap-2">
                          Lihat detail
                          <ChevronRight size={15} />
                        </span>
                      </div>
                    </button>
                  </article>
                );
              })}
            </div>
          </section>
        )}

        {/* Hasil kosong */}
        {!loading && !error && queryUrl && hasil.length === 0 && (
          <div className="mt-8 rounded-3xl border border-slate-200 bg-white px-6 py-12 text-center shadow-sm">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100">
              <Search size={25} className="text-slate-400" />
            </div>

            <h2 className="mt-5 text-lg font-bold text-slate-900">
              Belum ada hasil rekomendasi
            </h2>

            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
              Coba gunakan kata kunci yang berbeda, misalnya pasir putih, ombak
              tenang, atau pantai untuk keluarga.
            </p>

            <Link
              to="/"
              className="mt-5 inline-flex items-center gap-2 rounded-xl bg-sky-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-sky-700"
            >
              Kembali ke pencarian
              <ChevronRight size={16} />
            </Link>
          </div>
        )}

        {/* Belum mencari */}
        {!loading && !error && !queryUrl && (
          <div className="mt-8 rounded-3xl border border-slate-200 bg-white px-6 py-12 text-center shadow-sm">
            <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-2xl bg-sky-50">
              <Waves size={27} className="text-sky-600" />
            </div>

            <h2 className="mt-5 text-lg font-bold text-slate-900">
              Pantai impianmu menunggu
            </h2>

            <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-500">
              Masukkan preferensi pantai pada kolom pencarian untuk mendapatkan
              rekomendasi yang sesuai.
            </p>

            <Link
              to="/"
              className="mt-5 inline-flex items-center gap-2 rounded-xl bg-sky-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-sky-700"
            >
              Mulai pencarian
              <ChevronRight size={16} />
            </Link>
          </div>
        )}
      </div>

      {/* ================================================= */}
      {/* MODAL DETAIL PANTAI */}
      {/* ================================================= */}

      {pantaiTerpilih && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 p-3 backdrop-blur-sm sm:p-6"
          onClick={() => setPantaiTerpilih(null)}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="judul-modal-pantai"
            className="relative max-h-[92vh] w-full max-w-2xl overflow-y-auto rounded-3xl bg-white shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Tombol tutup */}
            <button
              type="button"
              onClick={() => setPantaiTerpilih(null)}
              aria-label="Tutup detail pantai"
              className="absolute right-4 top-4 z-10 flex h-10 w-10 items-center justify-center rounded-full bg-white/90 text-slate-700 shadow-md backdrop-blur transition hover:bg-white hover:text-red-600"
            >
              <X size={20} />
            </button>

            {/* Foto pantai */}
            <div className="relative h-56 bg-slate-100 sm:h-72">
              {pantaiTerpilih.foto_url ? (
                <img
                  src={pantaiTerpilih.foto_url}
                  alt={pantaiTerpilih.pantai}
                  className="h-full w-full object-cover"
                />
              ) : (
                <div className="flex h-full flex-col items-center justify-center gap-2 text-slate-400">
                  <Waves size={42} />
                  <span className="text-sm">Foto pantai belum tersedia</span>
                </div>
              )}

              <div className="absolute inset-x-0 bottom-0 h-28 bg-gradient-to-t from-black/60 to-transparent" />

              <div className="absolute bottom-5 left-5 right-5">
                <span className="inline-flex rounded-full bg-sky-600 px-3 py-1 text-xs font-bold text-white">
                  DETAIL REKOMENDASI
                </span>

                <h2
                  id="judul-modal-pantai"
                  className="mt-2 text-2xl font-extrabold text-white sm:text-3xl"
                >
                  {pantaiTerpilih.pantai}
                </h2>
              </div>
            </div>

            {/* Konten modal */}
            <div className="space-y-6 p-5 sm:p-7">
              {/* Lokasi */}
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <MapPin size={17} className="text-sky-600" />
                Malang Selatan
              </div>

              {/* Deskripsi */}
              <section>
                <h3 className="text-base font-bold text-slate-900">
                  Tentang Pantai
                </h3>

                <p className="mt-2 text-sm leading-7 text-slate-600">
                  {pantaiTerpilih.deskripsi ||
                    "Deskripsi pantai belum tersedia."}
                </p>
              </section>

              {/* Informasi jarak */}
              <section className="rounded-2xl border border-sky-100 bg-sky-50/70 p-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-white text-sky-600 shadow-sm">
                    <Navigation size={20} />
                  </div>

                  <div className="min-w-0 flex-1">
                    <h3 className="text-sm font-bold text-slate-900">
                      Jarak dari lokasi Anda
                    </h3>

                    {lokasiPengguna ? (
                      jarakModal !== null ? (
                        <p className="mt-1 text-xl font-extrabold tabular-nums text-sky-700">
                          {jarakModal.toFixed(2)} km
                        </p>
                      ) : (
                        <p className="mt-1 text-sm text-slate-500">
                          Koordinat pantai tidak tersedia.
                        </p>
                      )
                    ) : (
                      <p className="mt-1 text-sm leading-5 text-slate-500">
                        Aktifkan lokasi untuk mengetahui jarak pantai dari
                        tempat Anda.
                      </p>
                    )}
                  </div>
                </div>

                {!lokasiPengguna && (
                  <button
                    type="button"
                    onClick={aktifkanLokasi}
                    disabled={loadingLokasi || loadingKoordinat}
                    className="mt-4 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-sky-600 px-4 py-3 text-sm font-semibold text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:opacity-60"
                  >
                    {loadingLokasi ? (
                      <RefreshCw size={16} className="animate-spin" />
                    ) : (
                      <LocateFixed size={16} />
                    )}

                    {loadingLokasi ? "Mengambil lokasi..." : "Aktifkan Lokasi"}
                  </button>
                )}

                {lokasiPengguna && (
                  <p className="mt-3 text-xs leading-5 text-slate-500">
                    Jarak merupakan perhitungan geografis garis lurus, bukan
                    jarak perjalanan kendaraan.
                  </p>
                )}

                {statusLokasi && !lokasiPengguna && (
                  <p className="mt-3 text-xs leading-5 text-amber-700">
                    {statusLokasi}
                  </p>
                )}
              </section>

              {/* Rincian skor */}
              <section>
                <div className="mb-4">
                  <h3 className="text-base font-bold text-slate-900">
                    Rincian Skor Rekomendasi
                  </h3>

                  <p className="mt-1 text-xs leading-5 text-slate-500">
                    Nilai yang digunakan sistem untuk menentukan tingkat
                    kecocokan pantai.
                  </p>
                </div>

                <div className="space-y-4 rounded-2xl border border-slate-200 bg-white p-4">
                  {/* Cosine Similarity */}
                  <div>
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="text-sm font-semibold text-slate-700">
                          Cosine Similarity
                        </p>
                        <p className="mt-0.5 text-xs text-slate-400">
                          Content-Based Filtering
                        </p>
                      </div>

                      <span className="text-sm font-bold tabular-nums text-slate-800">
                        {(Number(pantaiTerpilih.skor_cosine) || 0).toFixed(4)}
                      </span>
                    </div>

                    <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full bg-blue-500 transition-all"
                        style={{
                          width: `${Math.max(
                            0,
                            Math.min(
                              100,
                              (Number(pantaiTerpilih.skor_cosine) || 0) * 100,
                            ),
                          )}%`,
                        }}
                      />
                    </div>
                  </div>

                  {/* BWR */}
                  <div>
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="text-sm font-semibold text-slate-700">
                          Bayesian Weighted Rating
                        </p>
                        <p className="mt-0.5 text-xs text-slate-400">
                          Rating Aggregation
                        </p>
                      </div>

                      <span className="text-sm font-bold tabular-nums text-slate-800">
                        {(Number(pantaiTerpilih.skor_bwr) || 0).toFixed(4)}
                      </span>
                    </div>

                    <div className="mt-2 h-2 overflow-hidden rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full bg-emerald-500 transition-all"
                        style={{
                          width: `${Math.max(
                            0,
                            Math.min(
                              100,
                              (Number(pantaiTerpilih.skor_bwr) || 0) * 100,
                            ),
                          )}%`,
                        }}
                      />
                    </div>
                  </div>

                  {/* Skor akhir */}
                  <div className="rounded-xl bg-sky-50 p-4">
                    <div className="flex items-center justify-between gap-3">
                      <div>
                        <p className="text-sm font-bold text-sky-900">
                          Skor Akhir
                        </p>
                        <p className="mt-0.5 text-xs text-sky-700">
                          Hasil perhitungan hybrid
                        </p>
                      </div>

                      <span className="text-2xl font-extrabold tabular-nums text-sky-700">
                        {formatPersen(pantaiTerpilih.skor_akhir)}
                      </span>
                    </div>

                    <div className="mt-3 h-2 overflow-hidden rounded-full bg-white">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-sky-400 to-sky-600 transition-all"
                        style={{
                          width: `${Math.max(
                            0,
                            Math.min(
                              100,
                              (Number(pantaiTerpilih.skor_akhir) || 0) * 100,
                            ),
                          )}%`,
                        }}
                      />
                    </div>
                  </div>
                </div>
              </section>

              {/* Keterangan metode */}
              <div className="flex items-start gap-2 rounded-xl bg-slate-50 p-3 text-xs leading-5 text-slate-500">
                <Database size={16} className="mt-0.5 shrink-0 text-sky-600" />

                <p>
                  Sistem menggunakan metode Hybrid Recommendation yang
                  menggabungkan Content-Based Filtering dan Rating Aggregation.
                  Skor akhir mengikuti hasil perhitungan dari backend.
                </p>
              </div>

              {/* Tombol tutup */}
              <button
                type="button"
                onClick={() => setPantaiTerpilih(null)}
                className="w-full rounded-xl bg-slate-900 px-5 py-3.5 text-sm font-semibold text-white transition hover:bg-slate-700"
              >
                Tutup Detail
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
