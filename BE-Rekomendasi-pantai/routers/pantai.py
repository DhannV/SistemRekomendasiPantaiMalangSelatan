
import time
import traceback

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database import engine
from services.rekomendasi import (
    rekomendasikan_pantai,
    model_sudah_disiapkan,
)


# =========================================================
# 1. KONFIGURASI ROUTER
# =========================================================

router = APIRouter(
    prefix="/pantai",
    tags=["Pantai"],
)


# =========================================================
# 2. VALIDASI PERMINTAAN REKOMENDASI
# =========================================================

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


# =========================================================
# 3. ENDPOINT DAFTAR PANTAI
# =========================================================

@router.get("/daftar")
def get_daftar_pantai():
    """
    Mengambil daftar nama pantai yang tersedia
    dari database Supabase.
    """

    query = text("""
        SELECT DISTINCT pantai
        FROM public.dataset_pantai
        WHERE pantai IS NOT NULL
          AND TRIM(pantai) <> ''
        ORDER BY pantai ASC
    """)

    try:
        with engine.connect() as connection:
            hasil = (
                connection.execute(query)
                .mappings()
                .all()
            )

        daftar = [
            row["pantai"]
            for row in hasil
        ]

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


# =========================================================
# 4. ENDPOINT REKOMENDASI PANTAI
# =========================================================

@router.post("/rekomendasi")
def post_rekomendasi_pantai(
    permintaan: PermintaanRekomendasi,
):
    """
    Menghasilkan rekomendasi pantai berdasarkan
    preferensi pengguna.

    Model TF-IDF dan BWR sudah dimuat dari file Joblib
    ketika aplikasi FastAPI dijalankan.

    Endpoint ini hanya melakukan preprocessing query,
    cosine similarity, dan perhitungan skor hybrid.
    """

    waktu_mulai = time.perf_counter()

    try:

        # -------------------------------------------------
        # 1. Memastikan model sudah dimuat
        # -------------------------------------------------

        if not model_sudah_disiapkan():
            print(
                "[ERROR] Model rekomendasi belum tersedia.",
                flush=True,
            )

            raise HTTPException(
                status_code=503,
                detail=(
                    "Model rekomendasi belum tersedia. "
                    "Silakan coba beberapa saat lagi."
                ),
            )

        waktu_model_siap = time.perf_counter()

        # -------------------------------------------------
        # 2. Menghitung rekomendasi
        # -------------------------------------------------

        hasil = rekomendasikan_pantai(
            query=permintaan.query,
            top_n=permintaan.top_n,
        )

        waktu_selesai = time.perf_counter()

        # -------------------------------------------------
        # 3. Logging performa
        # -------------------------------------------------

        print(
            f"[PERFORMA] Rekomendasi selesai | "
            f"Query: {permintaan.query!r} | "
            f"Jumlah hasil: {hasil['jumlah_hasil']} | "
            f"Pemeriksaan model: "
            f"{waktu_model_siap - waktu_mulai:.4f} detik | "
            f"Perhitungan query: "
            f"{waktu_selesai - waktu_model_siap:.4f} detik | "
            f"Total: {waktu_selesai - waktu_mulai:.4f} detik",
            flush=True,
        )

        # -------------------------------------------------
        # 4. Mengembalikan hasil
        # -------------------------------------------------

        return {
            "status": "success",
            **hasil,
        }

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except RuntimeError as error:
        print(
            f"[ERROR] Model rekomendasi: {error}",
            flush=True,
        )

        raise HTTPException(
            status_code=503,
            detail="Model rekomendasi belum siap digunakan.",
        )

    except Exception:
        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                "Terjadi kesalahan saat memproses "
                "rekomendasi pantai."
            ),
        )


# =========================================================
# 5. ENDPOINT KOORDINAT PANTAI
# =========================================================

@router.get("/koordinat")
def get_koordinat_pantai():
    """
    Mengambil koordinat seluruh pantai
    dari tabel data_pantai.
    """

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
            hasil = (
                connection.execute(query)
                .mappings()
                .all()
            )

        data = [
            {
                "pantai": row["pantai"],
                "latitude": (
                    float(row["latitude"])
                    if row["latitude"] is not None
                    else None
                ),
                "longitude": (
                    float(row["longitude"])
                    if row["longitude"] is not None
                    else None
                ),
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
            detail=(
                "Gagal mengambil koordinat pantai dari database."
            ),
        )
