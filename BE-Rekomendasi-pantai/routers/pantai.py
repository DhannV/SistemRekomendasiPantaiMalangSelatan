
import time
import traceback

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from database import engine
from routers.auth import require_admin

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
# 2. VALIDASI PERMINTAAN
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


class TambahPantaiRequest(BaseModel):
    nama_pantai: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Nama pantai yang akan ditambahkan",
    )


# =========================================================
# 3. ENDPOINT DAFTAR PANTAI
# =========================================================

@router.get("/daftar")
def get_daftar_pantai():
    """
    Mengambil daftar nama pantai dari pantai_master.
    """

    query = text("""
        SELECT nama_pantai
        FROM public.pantai_master
        ORDER BY nama_pantai ASC
    """)

    try:
        with engine.connect() as connection:
            hasil = connection.execute(query).mappings().all()

        daftar = [
            row["nama_pantai"]
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
# 4. ENDPOINT ADMIN - MENGAMBIL DAFTAR PANTAI
# =========================================================

@router.get("/admin/daftar")
def get_daftar_pantai_admin(
    current_user: dict = Depends(require_admin),
):
    """
    Mengambil daftar pantai beserta ID untuk keperluan CRUD admin.
    """

    query = text("""
        SELECT
            id,
            nama_pantai,
            created_at
        FROM public.pantai_master
        ORDER BY nama_pantai ASC
    """)

    try:
        with engine.connect() as connection:
            hasil = connection.execute(query).mappings().all()

        data = [
            dict(row)
            for row in hasil
        ]

        return {
            "status": "success",
            "jumlah_pantai": len(data),
            "data": data,
        }

    except SQLAlchemyError:
        print(
            "[ERROR] Gagal mengambil data pantai admin.",
            flush=True,
        )

        raise HTTPException(
            status_code=500,
            detail="Gagal mengambil data pantai.",
        )


# =========================================================
# 5. ENDPOINT ADMIN - TAMBAH PANTAI
# =========================================================

@router.post("/admin", status_code=201)
def tambah_pantai(
    permintaan: TambahPantaiRequest,
    current_user: dict = Depends(require_admin),
):
    """
    Menambahkan pantai baru ke pantai_master.
    """

    nama_pantai = permintaan.nama_pantai.strip()

    if not nama_pantai:
        raise HTTPException(
            status_code=400,
            detail="Nama pantai tidak boleh kosong.",
        )

    query = text("""
        INSERT INTO public.pantai_master (nama_pantai)
        VALUES (:nama_pantai)
        RETURNING id, nama_pantai, created_at
    """)

    try:
        with engine.begin() as connection:
            hasil = connection.execute(
                query,
                {"nama_pantai": nama_pantai},
            ).mappings().one()

        print(
            f"[ADMIN] Pantai berhasil ditambahkan: {nama_pantai}",
            flush=True,
        )

        return {
            "status": "success",
            "message": "Pantai berhasil ditambahkan.",
            "data": dict(hasil),
        }

    except IntegrityError:
        raise HTTPException(
            status_code=409,
            detail="Nama pantai sudah terdaftar.",
        )

    except SQLAlchemyError:
        print(
            "[ERROR] Gagal menambahkan pantai.",
            flush=True,
        )

        raise HTTPException(
            status_code=500,
            detail="Gagal menyimpan data pantai.",
        )


# =========================================================
# 6. ENDPOINT ADMIN - HAPUS PANTAI
# =========================================================

@router.delete("/admin/{pantai_id}")
def hapus_pantai(
    pantai_id: int,
    current_user: dict = Depends(require_admin),
):
    """
    Menghapus pantai berdasarkan ID dari pantai_master.

    Tidak menghapus data dari dataset_pantai maupun data_pantai.
    """

    query = text("""
        DELETE FROM public.pantai_master
        WHERE id = :pantai_id
        RETURNING id, nama_pantai
    """)

    try:
        with engine.begin() as connection:
            hasil = connection.execute(
                query,
                {"pantai_id": pantai_id},
            ).mappings().first()

            if not hasil:
                raise HTTPException(
                    status_code=404,
                    detail="Data pantai tidak ditemukan.",
                )

        print(
            f"[ADMIN] Pantai berhasil dihapus: {hasil['nama_pantai']}",
            flush=True,
        )

        return {
            "status": "success",
            "message": "Pantai berhasil dihapus.",
            "data": dict(hasil),
        }

    except HTTPException:
        raise

    except SQLAlchemyError:
        print(
            "[ERROR] Gagal menghapus pantai.",
            flush=True,
        )

        raise HTTPException(
            status_code=500,
            detail="Gagal menghapus data pantai.",
        )


# =========================================================
# 7. ENDPOINT REKOMENDASI PANTAI
# =========================================================

@router.post("/rekomendasi")
def post_rekomendasi_pantai(
    permintaan: PermintaanRekomendasi,
):

    waktu_mulai = time.perf_counter()

    try:

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

        hasil = rekomendasikan_pantai(
            query=permintaan.query,
            top_n=permintaan.top_n,
        )

        waktu_selesai = time.perf_counter()

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
# 8. ENDPOINT KOORDINAT PANTAI
# =========================================================

@router.get("/koordinat")
def get_koordinat_pantai():

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
            detail="Gagal mengambil koordinat pantai dari database.",
        )
