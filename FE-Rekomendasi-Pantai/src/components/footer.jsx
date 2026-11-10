import { Waves, MapPin, Compass, Heart, ArrowUpRight } from "lucide-react";

const Footer = () => {
  const year = new Date().getFullYear();

  const linkClass =
    "text-sm text-slate-500 transition-colors duration-200 hover:text-sky-600";

  return (
    <footer className="border-t border-slate-200 bg-[#F7F9FC] text-slate-900">
      <div className="mx-auto max-w-7xl px-6 pt-12 pb-6 lg:px-8">
        <div className="grid grid-cols-1 gap-10 sm:grid-cols-2 lg:grid-cols-4 lg:gap-12">
          {/* Brand */}
          <div className="lg:col-span-2">
            <a href="/" className="inline-flex items-center gap-3"></a>

            <p className="mt-5 max-w-md text-sm leading-7 text-slate-500">
              Temukan pantai yang cocok untuk caramu berlibur. Dapatkan
              rekomendasi berdasarkan preferensi kamu !
            </p>

            <div className="mt-4 flex items-center gap-2 text-sm text-slate-500">
              <MapPin size={17} className="text-sky-600" />
              Malang, Jawa Timur, Indonesia
            </div>
          </div>

          {/* Navigasi */}
          <div>
            <h3 className="mb-5 text-sm font-bold">Navigasi</h3>

            <ul className="space-y-3">
              <li>
                <a href="/" className={linkClass}>
                  Beranda
                </a>
              </li>
              <li>
                <a href="/" className={linkClass}>
                  Rekomendasi Pantai
                </a>
              </li>
              <li>
                <a href="/" className={linkClass}>
                  Tentang Website
                </a>
              </li>
            </ul>
          </div>

          {/* Jelajahi */}
          <div>
            <h3 className="mb-5 text-sm font-bold">Jelajahi</h3>

            <ul className="space-y-3">
              <li>
                <a href="/" className={linkClass}>
                  Cari Pantai
                </a>
              </li>
              <li>
                {/* <a href="/rekomendasi" className={linkClass}>
                  Temukan Destinasi
                </a> */}
              </li>
            </ul>

            <a
              href="/"
              className="mt-6 block rounded-xl border border-slate-200 bg-white p-4 transition-all duration-200 hover:-translate-y-0.5 hover:border-sky-200 hover:shadow-md hover:shadow-slate-200/50"
            >
              <div className="flex items-center justify-between gap-2">
                <span className="flex items-center gap-2 text-sm font-semibold">
                  <Compass size={18} className="text-sky-600" />
                  Cari pantai impian
                </span>
                <ArrowUpRight size={16} className="text-sky-600" />
              </div>

              <p className="mt-2 text-xs leading-5 text-slate-500">
                Temukan destinasi yang sesuai dengan preferensimu.
              </p>
            </a>
          </div>
        </div>

        {/* Copyright */}
        <div className="my-9 h-px bg-slate-200" />

        <div className="flex flex-col items-center justify-between gap-3 text-center sm:flex-row sm:text-left">
          <p className="text-xs text-slate-500">
            © {year} Pantai Malang. Semua hak dilindungi.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
