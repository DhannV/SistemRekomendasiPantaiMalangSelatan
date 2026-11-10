import React from "react";
import { Database, MapPin, Sparkles } from "lucide-react";

export default function StatistikData() {
  const stats = [
    { icon: MapPin, nilai: "40", label: "Pantai Terdata" },
    { icon: Database, nilai: "4.000 +", label: "Ulasan Diekstrak" },
    { icon: Sparkles, nilai: "Hybrid", label: "Metode Rekomendasi" },
  ];

  return (
    <section className="bg-slate-50 px-4 pb-12 sm:pb-16">
      <div className="mx-auto max-w-4xl -mt-8 relative z-10">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3 sm:gap-6 rounded-3xl bg-white p-6 md:p-8 shadow-xl shadow-slate-200/50 ring-1 ring-slate-100">
          {stats.map((stat, i) => {
            const Icon = stat.icon;
            return (
              <div
                key={i}
                className="flex flex-col items-center text-center p-4"
              >
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-sky-50 text-sky-600">
                  <Icon className="h-6 w-6" aria-hidden="true" />
                </div>
                <p className="text-3xl font-bold text-slate-900">
                  {stat.nilai}
                </p>
                <p className="mt-1 text-sm font-medium text-slate-500">
                  {stat.label}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
