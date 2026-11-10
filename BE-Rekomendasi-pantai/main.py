
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from routers.auth import router as auth_router
from routers.pantai import router as pantai_router
from routers import search_history
from routers.users import router as users_router
from routers.evaluasi import router as evaluasi_router

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database import engine, test_connection

app = FastAPI(
    title="API Rekomendasi Pantai Malang Selatan",
    description="Backend sistem rekomendasi pantai",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        # Domain utama Vercel
        "https://sistem-rekomendasi-pantai-malang-se.vercel.app",
        # Domain deployment Vercel
        "https://sistem-rekomendasi-pantai-malang-selatan-51zs7iw2j.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "API Rekomendasi Pantai berhasil dijalankan"
    }


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


@app.get("/pantai")
def get_pantai():
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("""
                    SELECT
                        pantai,
                        "user",
                        teks,
                        rating
                    FROM public.dataset_pantai
                    WHERE pantai IS NOT NULL
                      AND TRIM(pantai) <> ''
                    ORDER BY pantai
                """)
            )

            data = [
                dict(row)
                for row in result.mappings().all()
            ]

        # Mengelompokkan data berdasarkan nama pantai
        pantai_unik = {}

        for item in data:
            nama = str(item.get("pantai") or "").strip()

            if not nama:
                continue

            # Mengabaikan perbedaan huruf besar/kecil
            kunci = nama.casefold()

            if kunci not in pantai_unik:
                pantai_unik[kunci] = {
                    "pantai": nama,
                    "rating_list": [],
                    "ulasan": [],
                    "jumlah_ulasan": 0,
                    "users": [],
                }

            grup = pantai_unik[kunci]

            # Mengumpulkan rating yang valid
            rating = item.get("rating")

            if rating is not None:
                try:
                    nilai_rating = float(rating)

                    if 0 <= nilai_rating <= 5:
                        grup["rating_list"].append(nilai_rating)

                except (TypeError, ValueError):
                    pass

            # Mengumpulkan teks ulasan
            teks_ulasan = str(item.get("teks") or "").strip()

            if teks_ulasan:
                grup["ulasan"].append(teks_ulasan)

            # Mengumpulkan nama user
            nama_user = str(item.get("user") or "").strip()

            if nama_user and nama_user not in grup["users"]:
                grup["users"].append(nama_user)

            grup["jumlah_ulasan"] += 1

        # Membentuk hasil akhir satu baris per pantai
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

        # Mengurutkan nama pantai secara alfabetis
        hasil.sort(
            key=lambda item: item["pantai"].casefold()
        )

        return {
            "status": "success",
            "jumlah_data_asli": len(data),
            "jumlah_pantai": len(hasil),
            "data": hasil,
        }

    except SQLAlchemyError:
        raise HTTPException(
            status_code=500,
            detail="Gagal mengambil data pantai dari database."
        )

   
app.include_router(pantai_router)
app.include_router(auth_router)
app.include_router(search_history.router)
app.include_router(users_router)
app.include_router(evaluasi_router)