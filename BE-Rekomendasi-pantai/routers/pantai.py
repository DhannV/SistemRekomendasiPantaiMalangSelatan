
import time
from threading import Lock

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database import engine
from services.rekomendasi import (
    rekomendasikan_pantai,
    model_sudah_disiapkan,
    siapkan_model,
)


router = APIRouter(
    prefix="/pantai",
    tags=["Pantai"],
)

# Mencegah persiapan model ganda pada satu proses backend.
_model_lock = Lock()


class PermintaanRekomendasi(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Preferensi pantai yang ingin dicari",
        examples=["pantai pasir putih dengan ombak tenang"],
    )
    top_n: int = Field(
        default=5,
        ge=1,
        le=40,
        description="Jumlah rekomendasi yang ditampilkan",
    )


def ambil_data_model():
    """Mengambil data ulasan dan rating dari Supabase."""

    query_ulasan = text("""
        SELECT pantai, teks
        FROM public.dataset_pantai
        WHERE pantai IS NOT NULL
          AND TRIM(pantai) <> ''
          AND teks IS NOT NULL
          AND TRIM(teks) <> ''
    """)

    query_rating = text("""
        SELECT pantai, rating
        FROM public.dataset_pantai
        WHERE pantai IS NOT NULL
          AND TRIM(pantai) <> ''
          AND rating IS NOT NULL
    """)

    waktu_mulai = time.perf_counter()

    with engine.connect() as connection:
        hasil_ulasan = (
            connection.execute(query_ulasan)
            .mappings()
            .all()
        )

        hasil_rating = (
            connection.execute(query_rating)
            .mappings()
            .all()
        )

    data_ulasan = [
        {"pantai": row["pantai"], "teks": row["teks"]}
        for row in hasil_ulasan
    ]

    data_rating = [
        {"pantai": row["pantai"], "rating": row["rating"]}
        for row in hasil_rating
    ]

    durasi = time.perf_counter() - waktu_mulai

    print(
        f"[PERFORMA] Pengambilan database selesai | "
        f"Ulasan: {len(data_ulasan)} | "
        f"Rating: {len(data_rating)} | "
        f"Waktu: {durasi:.2f} detik",
        flush=True,
    )

    return data_ulasan, data_rating


def pastikan_model_siap():
    """Siapkan model hanya jika cache belum tersedia."""

    if model_sudah_disiapkan():
        return

    with _model_lock:
        # Periksa ulang setelah mendapatkan lock.
        if model_sudah_disiapkan():
            return

        waktu_mulai = time.perf_counter()

        data_ulasan, data_rating = ambil_data_model()
        waktu_database_selesai = time.perf_counter()

        siapkan_model(data_ulasan, data_rating)
        waktu_selesai = time.perf_counter()

        print(
            f"[PERFORMA] Persiapan model selesai | "
            f"Database: "
            f"{waktu_database_selesai - waktu_mulai:.2f} detik | "
            f"Model: "
            f"{waktu_selesai - waktu_database_selesai:.2f} detik | "
            f"Total: {waktu_selesai - waktu_mulai:.2f} detik",
            flush=True,
        )


@router.get("/daftar")
def get_daftar_pantai():
    """Mengambil daftar nama pantai yang tersedia."""

    query = text("""
        SELECT DISTINCT pantai
        FROM public.dataset_pantai
        WHERE pantai IS NOT NULL
          AND TRIM(pantai) <> ''
        ORDER BY pantai ASC
    """)

    try:
        with engine.connect() as connection:
            hasil = connection.execute(query).mappings().all()

        daftar = [row["pantai"] for row in hasil]

        return {
            "status": "success",
            "jumlah_pantai": len(daftar),
            "data": daftar,
        }

    except SQLAlchemyError:
        print(
            "[ERROR] Gagal mengambil daftar pantai.",
            flush=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Gagal mengambil daftar pantai.",
        )


@router.post("/rekomendasi")
def post_rekomendasi_pantai(
    permintaan: PermintaanRekomendasi,
):
    """Menghasilkan rekomendasi berdasarkan preferensi pengguna."""

    waktu_mulai = time.perf_counter()

    try:
        pastikan_model_siap()
        waktu_model_siap = time.perf_counter()

        hasil = rekomendasikan_pantai(
            query=permintaan.query,
            top_n=permintaan.top_n,
        )

        waktu_selesai = time.perf_counter()

        print(
            f"[PERFORMA] Rekomendasi selesai | "
            f"Query: {permintaan.query!r} | "
            f"Jumlah hasil: {hasil['jumlah_hasil']} | "
            f"Menunggu model: "
            f"{waktu_model_siap - waktu_mulai:.2f} detik | "
            f"Perhitungan query: "
            f"{waktu_selesai - waktu_model_siap:.2f} detik | "
            f"Total: {waktu_selesai - waktu_mulai:.2f} detik",
            flush=True,
        )

        return {
            "status": "success",
            **hasil,
        }

    except SQLAlchemyError:
        print(
            "[ERROR] Gagal mengambil data dari database.",
            flush=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Gagal mengambil data pantai dari database.",
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception:
        # Menampilkan traceback lengkap di terminal untuk debugging.
        import traceback
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail="Terjadi kesalahan saat memproses rekomendasi pantai.",
        )

@router.get("/koordinat")
def get_koordinat_pantai():
    """Mengambil koordinat seluruh pantai dari tabel data_pantai."""

    query = text("""
        SELECT
            pantai,
            latitude,
            longitude
        FROM public.data_pantai
        ORDER BY pantai ASC
    """)

    try:
        with engine.connect() as connection:
            hasil = connection.execute(query).mappings().all()

        data = [
            {
                "pantai": row["pantai"],
                "latitude": float(row["latitude"])
                if row["latitude"] is not None else None,
                "longitude": float(row["longitude"])
                if row["longitude"] is not None else None,
            }
            for row in hasil
        ]

        return {
            "status": "success",
            "jumlah_pantai": len(data),
            "data": data,
        }

    except SQLAlchemyError:
        print(
            "[ERROR] Gagal mengambil koordinat pantai.",
            flush=True,
        )
        raise HTTPException(
            status_code=500,
            detail="Gagal mengambil koordinat pantai dari database.",
        )