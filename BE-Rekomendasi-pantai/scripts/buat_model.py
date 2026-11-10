from pathlib import Path
import joblib
import time

from sqlalchemy import text

from database import engine
from services.rekomendasi import bangun_model


# Lokasi file model
ROOT_DIR = Path(__file__).resolve().parent.parent

FOLDER_MODEL = ROOT_DIR / "models"

FILE_MODEL = FOLDER_MODEL / "model_rekomendasi.joblib"


def ambil_data_model():
    """Mengambil data ulasan dan rating dari Supabase."""

    print("[DATA] Mengambil data dari Supabase...", flush=True)

    with engine.connect() as connection:

        # Mengambil data ulasan
        hasil_ulasan = connection.execute(
            text("""
                SELECT pantai, teks
                FROM public.dataset_pantai
                WHERE pantai IS NOT NULL
                  AND TRIM(pantai) <> ''
                  AND teks IS NOT NULL
                  AND TRIM(teks) <> ''
            """)
        )

        data_ulasan = [
            dict(row)
            for row in hasil_ulasan.mappings().all()
        ]

        # Mengambil data rating
        hasil_rating = connection.execute(
            text("""
                SELECT pantai, rating
                FROM public.dataset_pantai
                WHERE pantai IS NOT NULL
                  AND TRIM(pantai) <> ''
                  AND rating IS NOT NULL
            """)
        )

        data_rating = [
            dict(row)
            for row in hasil_rating.mappings().all()
        ]

    print(
        f"[DATA] Jumlah ulasan: {len(data_ulasan)}",
        flush=True,
    )

    print(
        f"[DATA] Jumlah rating: {len(data_rating)}",
        flush=True,
    )

    return data_ulasan, data_rating


def main():
    waktu_mulai = time.perf_counter()

    # 1. Mengambil data dari database
    data_ulasan, data_rating = ambil_data_model()

    if not data_ulasan:
        raise ValueError("Data ulasan kosong. Model tidak dapat dibuat.")

    # 2. Membentuk model
    model = bangun_model(
        data_ulasan=data_ulasan,
        data_rating=data_rating,
    )

    # 3. Membuat folder models jika belum tersedia
    FOLDER_MODEL.mkdir(parents=True, exist_ok=True)

    # 4. Menyimpan model menggunakan Joblib
    joblib.dump(
        model,
        FILE_MODEL,
        compress=3,
    )

    waktu_total = time.perf_counter() - waktu_mulai

    print("\n===================================")
    print("[MODEL] MODEL BERHASIL DIBUAT")
    print("===================================")
    print(f"Lokasi: {FILE_MODEL}")
    print(f"Jumlah pantai: {len(model['vektor_pantai'])}")
    print(f"Jumlah kosakata: {len(model['kosakata'])}")
    print(f"Waktu total: {waktu_total:.2f} detik")
    print("===================================")


if __name__ == "__main__":
    main()