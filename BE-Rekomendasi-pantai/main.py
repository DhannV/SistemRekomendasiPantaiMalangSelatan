
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database import engine, test_connection
from services.model_loader import muat_model

from routers.auth import router as auth_router
from routers.pantai import router as pantai_router
from routers import search_history
from routers.users import router as users_router
from routers.evaluasi import router as evaluasi_router


# =========================================================
# 1. LIFESPAN FASTAPI
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Menjalankan proses pemuatan model ketika FastAPI startup.

    Model hanya dimuat satu kali pada setiap proses backend.
    """

    print("[STARTUP] Memulai aplikasi FastAPI...", flush=True)

    try:
        muat_model()

        print(
            "[STARTUP] Model rekomendasi siap digunakan.",
            flush=True,
        )

    except Exception as error:
        print(
            f"[STARTUP ERROR] Gagal memuat model: {error}",
            flush=True,
        )

        raise

    yield

    print("[SHUTDOWN] Aplikasi FastAPI dihentikan.", flush=True)


# =========================================================
# 2. KONFIGURASI APLIKASI FASTAPI
# =========================================================

app = FastAPI(
    title="API Rekomendasi Pantai Malang Selatan",
    description="Backend sistem rekomendasi pantai",
    version="1.0.0",
    lifespan=lifespan,
)


# =========================================================
# 3. KONFIGURASI CORS
# =========================================================

origins = [
    "http://localhost:5173",
    "https://sistem-rekomendasi-pantai-malang-se.vercel.app",
    "https://sistem-rekomendasi-pantai-malang-selatan-51zs7iw2j.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)


# =========================================================
# 4. ENDPOINT HOME
# =========================================================

@app.get("/")
def home():
    return {
        "message": "API Rekomendasi Pantai berhasil dijalankan"
    }


# =========================================================
# 5. TEST KONEKSI DATABASE
# =========================================================

@app.get("/db-test")
def database_test():
    try:
        version = test_connection()

        return {
            "status": "success",
            "message": "Berhasil terhubung ke Supabase",
            "database": "PostgreSQL",
            "version": version,
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Koneksi database gagal. Periksa konfigurasi."
        )


# =========================================================
# 6. MENGAMBIL DATA PANTAI
# =========================================================


@app.get("/pantai")
def get_pantai():
    try:
        with engine.connect() as connection:

            # Mengambil seluruh pantai yang masih aktif.
            result_master = connection.execute(
                text("""
                    SELECT nama_pantai
                    FROM public.pantai_master
                    WHERE nama_pantai IS NOT NULL
                      AND TRIM(nama_pantai) <> ''
                    ORDER BY nama_pantai
                """)
            )

            daftar_master = [
                dict(row)
                for row in result_master.mappings().all()
            ]

            # Mengambil ulasan hanya untuk pantai yang masih aktif.
            result_ulasan = connection.execute(
                text("""
                    SELECT
                        dp.pantai,
                        dp."user",
                        dp.teks,
                        dp.rating
                    FROM public.dataset_pantai dp
                    INNER JOIN public.pantai_master pm
                        ON LOWER(TRIM(dp.pantai)) =
                           LOWER(TRIM(pm.nama_pantai))
                    WHERE dp.pantai IS NOT NULL
                      AND TRIM(dp.pantai) <> ''
                    ORDER BY dp.pantai
                """)
            )

            data = [
                dict(row)
                for row in result_ulasan.mappings().all()
            ]

        # Membuat kelompok berdasarkan pantai master.
        pantai_unik = {}

        for item in daftar_master:
            nama = str(item.get("nama_pantai") or "").strip()

            if not nama:
                continue

            kunci = nama.casefold()

            pantai_unik[kunci] = {
                "pantai": nama,
                "rating_list": [],
                "ulasan": [],
                "jumlah_ulasan": 0,
                "users": [],
            }

        # Memasukkan ulasan ke kelompok pantai yang sesuai.
        for item in data:
            nama = str(item.get("pantai") or "").strip()

            if not nama:
                continue

            kunci = nama.casefold()

            if kunci not in pantai_unik:
                continue

            grup = pantai_unik[kunci]

            # Mengumpulkan rating yang valid.
            rating = item.get("rating")

            if rating is not None:
                try:
                    nilai_rating = float(rating)

                    if 0 <= nilai_rating <= 5:
                        grup["rating_list"].append(nilai_rating)

                except (TypeError, ValueError):
                    pass

            # Mengumpulkan teks ulasan.
            teks_ulasan = str(item.get("teks") or "").strip()

            if teks_ulasan:
                grup["ulasan"].append(teks_ulasan)

            # Mengumpulkan nama user.
            nama_user = str(item.get("user") or "").strip()

            if nama_user and nama_user not in grup["users"]:
                grup["users"].append(nama_user)

            grup["jumlah_ulasan"] += 1

        # Membentuk hasil akhir.
        hasil = []

        for grup in pantai_unik.values():
            daftar_rating = grup["rating_list"]

            rata_rata_rating = (
                round(sum(daftar_rating) / len(daftar_rating), 2)
                if daftar_rating
                else None
            )

            hasil.append({
                "pantai": grup["pantai"],
                "user": ", ".join(grup["users"]) or "-",
                "rating": rata_rata_rating,
                "teks": " | ".join(grup["ulasan"]) or "-",
                "jumlah_ulasan": grup["jumlah_ulasan"],
            })

        hasil.sort(
            key=lambda item: item["pantai"].casefold()
        )

        return {
            "status": "success",
            "jumlah_data_asli": len(data),
            "jumlah_pantai": len(hasil),
            "data": hasil,
        }

    except SQLAlchemyError as error:
        print(f"[ERROR GET PANTAI] {error}", flush=True)

        raise HTTPException(
            status_code=500,
            detail="Gagal mengambil data pantai dari database."
        )



# =========================================================
# 7. REGISTRASI ROUTER
# =========================================================

app.include_router(auth_router)
app.include_router(pantai_router)
app.include_router(search_history.router)
app.include_router(users_router)
app.include_router(evaluasi_router)
