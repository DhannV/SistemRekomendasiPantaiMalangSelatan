import React from "react";
import { MessageSquareText, Cpu, BarChart3 } from "lucide-react";

export default function CaraKerja() {
  const steps = [
    {
      title: "Masukkan Preferensi",
      desc: "Ketik suasana atau fasilitas yang Anda inginkan (misal: pasir putih, akses mudah, cocok untuk anak).",
      icon: MessageSquareText,
    },
    {
      title: "Analisis Ulasan",
      desc: "Sistem mencocokkan kata kunci Anda dengan profil teks dari ribuan ulasan pantai menggunakan algoritma TF-IDF , Cosine Similarity ,dan Rating Aggregation.",
      icon: Cpu,
    },
    {
      title: "Skor Hybrid",
      desc: "Kecocokan teks digabungkan dengan normalisasi rating (Bayesian Weighted Average) untuk memberikan rekomendasi.",
      icon: BarChart3,
    },
  ];

  return (
    <section className="bg-white px-4 py-16 sm:py-24">
      <div className="mx-auto max-w-6xl">
        <div className="mx-auto max-w-2xl text-center mb-16">
          <h2 className="text-base font-semibold leading-7 text-sky-600">
            Di Balik Layar
          </h2>
          <p className="mt-2 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
            Bagaimana sistem ini bekerja?
          </p>
        </div>

        <div className="grid grid-cols-1 gap-12 sm:grid-cols-3 relative">
          {/* Garis konektor background (Desktop Only) */}
          <div className="hidden sm:block absolute top-10 left-[15%] right-[15%] h-0.5 bg-slate-100 -z-10"></div>

          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div
                key={index}
                className="flex flex-col items-center text-center"
              >
                <div className="mb-6 flex h-20 w-20 items-center justify-center rounded-3xl bg-white shadow-lg shadow-sky-100 ring-1 ring-slate-100">
                  <Icon className="h-8 w-8 text-sky-600" aria-hidden="true" />
                </div>
                <h3 className="mb-3 text-xl font-bold text-slate-900">
                  {step.title}
                </h3>
                <p className="text-base leading-relaxed text-slate-600">
                  {step.desc}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
