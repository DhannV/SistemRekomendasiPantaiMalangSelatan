import React from "react";
import { Star, ArrowRight } from "lucide-react";

const daftarPantai = [
  {
    id: 1,
    nama: "Pantai Balekambang",
    rating: 4.8,
    ulasan: 1205,
    tags: ["Pasir Putih", "Pura Iconik"],
  },
  {
    id: 2,
    nama: "Pantai Sendang Biru",
    rating: 4.7,
    ulasan: 980,
    tags: ["Pelelangan Ikan", "Perahu"],
  },
  {
    id: 3,
    nama: "Pantai Tiga Warna",
    rating: 4.9,
    ulasan: 850,
    tags: ["Konservasi", "Snorkeling"],
  },
];

export default function PantaiUnggulan() {
  return (
    <section className="bg-slate-50 px-4 py-16 sm:py-24">
      <div className="mx-auto max-w-6xl">
        <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-end mb-10 md:mb-14">
          <div>
            <h2 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
              Rekomendasi Teratas
            </h2>
            <p className="mt-3 text-lg text-slate-600 max-w-2xl">
              Pantai dengan nilai ulasan tertinggi dari para pengunjung di
              Google Maps.
            </p>
          </div>
          <button className="group flex items-center gap-2 text-sm font-semibold text-sky-600 hover:text-sky-700 transition-colors">
            Lihat semua pantai
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
          </button>
        </div>

        <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          {daftarPantai.map((pantai) => (
            <div
              key={pantai.id}
              className="group flex flex-col overflow-hidden rounded-2xl bg-white shadow-sm ring-1 ring-slate-200 transition-all hover:shadow-lg hover:shadow-sky-100"
            >
              {/* Gambar (Placeholder) */}
              <div className="aspect-[4/3] bg-slate-200 relative overflow-hidden">
                <div className="absolute inset-0 flex items-center justify-center text-slate-500 font-medium bg-slate-100 group-hover:scale-105 transition-transform duration-500">
                  Cover {pantai.nama}
                </div>
              </div>

              <div className="flex flex-1 flex-col p-6">
                <div className="flex items-start justify-between gap-4 mb-2">
                  <h3 className="text-xl font-bold text-slate-900 line-clamp-1">
                    {pantai.nama}
                  </h3>
                  <div className="flex items-center gap-1 rounded-full bg-amber-50 px-2 py-1 ring-1 ring-amber-200/50 shrink-0">
                    <Star className="h-3.5 w-3.5 fill-amber-400 text-amber-400" />
                    <span className="text-xs font-bold text-amber-900">
                      {pantai.rating}
                    </span>
                  </div>
                </div>

                <p className="text-sm text-slate-500 mb-6">
                  Dari {pantai.ulasan.toLocaleString("id-ID")} ulasan
                </p>

                <div className="mt-auto flex flex-wrap gap-2">
                  {pantai.tags.map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center rounded-full bg-sky-50 px-2.5 py-1 text-xs font-medium text-sky-700 ring-1 ring-inset ring-sky-600/20"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
