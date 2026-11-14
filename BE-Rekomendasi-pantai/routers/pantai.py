
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
        description="Nama pantai",
    )

    deskripsi: str | None = Field(
        default=None,
        description="Deskripsi pantai",
    )

    foto_url: str | None = Field(
        default=None,
        description="URL foto pantai",
    )


# =========================================================
# 3. HELPER DATABASE
# =========================================================

def ambil_daftar_pantai_aktif():
    """
    Mengambil seluruh nama pantai yang terdaftar
    di tabel pantai_master.
    """

    query = text("""
        SELECT nama_pantai
        FROM public.pantai_master
        ORDER BY nama_pantai ASC
    """)

    with engine.connect() as connection:
        hasil = connection.execute(query).mappings().all()

    return [
        row["nama_pantai"]
        for row in hasil
        if row["nama_pantai"]
    ]


def ambil_semua_detail_pantai():
    """
    Mengambil nama, deskripsi, dan foto seluruh pantai.

    Data digunakan untuk melengkapi hasil rekomendasi
    tanpa melakukan query berulang.
    """

    query = text("""
        SELECT
            nama_pantai,
            deskripsi,
            foto_url
        FROM public.pantai_master
    """)

    with engine.connect() as connection:
        hasil = connection.execute(query).mappings().all()

    detail = {}

    for row in hasil:
        nama = row["nama_pantai"]

        if not nama:
            continue

        kunci = str(nama).strip().casefold()

        detail[kunci] = {
            "deskripsi": row["deskripsi"],
            "foto_url": row["foto_url"],
        }

    return detail


# =========================================================
# 4. ENDPOINT DAFTAR PANTAI
# =========================================================

@router.get("/daftar")
def get_daftar_pantai():
    try:
        daftar = ambil_daftar_pantai_aktif()

        return {
            "status": "success",
            "jumlah_pantai": len(daftar),
            "data": daftar,
        }

    except SQLAlchemyError as error:
        print(
            f"[ERROR] Daftar pantai: {error}",
            flush=True,
        )

        raise HTTPException(
            status_code=500,
            detail="Gagal mengambil daftar pantai.",
        )


# =========================================================
# 5. ENDPOINT ADMIN - DAFTAR PANTAI
# =========================================================

@router.get("/admin/daftar")
def get_daftar_pantai_admin(
    current_user: dict = Depends(require_admin),
):
    query = text("""
        SELECT
            id,
            nama_pantai,
            created_at,
            deskripsi,
            foto_url
        FROM public.pantai_master
        ORDER BY nama_pantai ASC
    """)

    try:
        with engine.connect() as connection:
            hasil = connection.execute(
                query
            ).mappings().all()

        data = [
            dict(row)
            for row in hasil
        ]

        return {
            "status": "success",
            "jumlah_pantai": len(data),
            "data": data,
        }

    except SQLAlchemyError as error:
        print(
            f"[ERROR] Daftar pantai admin: {error}",
            flush=True,
        )

        raise HTTPException(
            status_code=500,
            detail="Gagal mengambil data pantai.",
        )


# =========================================================
# 6. ENDPOINT ADMIN - TAMBAH PANTAI
# =========================================================

@router.post("/admin", status_code=201)
def tambah_pantai(
    permintaan: TambahPantaiRequest,
    current_user: dict = Depends(require_admin),
):
    nama_pantai = permintaan.nama_pantai.strip()

    if not nama_pantai:
        raise HTTPException(
            status_code=400,
            detail="Nama pantai tidak boleh kosong.",
        )

    query = text("""
        INSERT INTO public.pantai_master (
            nama_pantai,
            deskripsi,
            foto_url
        )
        VALUES (
            :nama_pantai,
            :deskripsi,
            :foto_url
        )
        RETURNING
            id,
            nama_pantai,
            created_at,
            deskripsi,
            foto_url
    """)

    try:
        with engine.begin() as connection:
            hasil = connection.execute(
                query,
                {
                    "nama_pantai": nama_pantai,
                    "deskripsi": permintaan.deskripsi,
                    "foto_url": permintaan.foto_url,
                },
            ).mappings().one()

        print(
            f"[ADMIN] Pantai ditambahkan: {nama_pantai}",
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

    except SQLAlchemyError as error:
        print(
            f"[ERROR] Tambah pantai: {error}",
            flush=True,
        )

        raise HTTPException(
            status_code=500,
            detail="Gagal menyimpan data pantai.",
        )


# =========================================================
# 7. ENDPOINT ADMIN - HAPUS PANTAI
# =========================================================

@router.delete("/admin/{pantai_id}")
def hapus_pantai(
    pantai_id: int,
    current_user: dict = Depends(require_admin),
):
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
            f"[ADMIN] Pantai dihapus: {hasil['nama_pantai']}",
            flush=True,
        )

        return {
            "status": "success",
            "message": (
                "Pantai berhasil dihapus dari daftar aktif. "
                "Data ulasan dan koordinat tetap tersimpan."
            ),
            "data": dict(hasil),
        }

    except HTTPException:
        raise

    except SQLAlchemyError as error:
        print(
            f"[ERROR] Hapus pantai: {error}",
            flush=True,
        )

        raise HTTPException(
            status_code=500,
            detail="Gagal menghapus data pantai.",
        )


# =========================================================
# 8. ENDPOINT REKOMENDASI PANTAI
# =========================================================

@router.post("/rekomendasi")
def post_rekomendasi_pantai(
    permintaan: PermintaanRekomendasi,
):
    waktu_mulai = time.perf_counter()

    try:
        # ---------------------------------------------
        # 1. Memastikan model tersedia
        # ---------------------------------------------

        if not model_sudah_disiapkan():
            raise HTTPException(
                status_code=503,
                detail="Model rekomendasi belum tersedia.",
            )

        # ---------------------------------------------
        # 2. Mengambil daftar pantai aktif
        # ---------------------------------------------

        daftar_pantai_aktif = ambil_daftar_pantai_aktif()

        waktu_database = time.perf_counter()

        # ---------------------------------------------
        # 3. Menghitung rekomendasi
        # ---------------------------------------------

        hasil = rekomendasikan_pantai(
            query=permintaan.query,
            top_n=permintaan.top_n,
            daftar_pantai_aktif=daftar_pantai_aktif,
        )

        # ---------------------------------------------
        # 4. Mengambil detail pantai
        # ---------------------------------------------

        detail_pantai = ambil_semua_detail_pantai()

        # ---------------------------------------------
        # 5. Menggabungkan detail dengan rekomendasi
        # ---------------------------------------------

        for item in hasil.get("data", []):
            nama_key = str(
                item["pantai"]
            ).strip().casefold()

            detail = detail_pantai.get(
                nama_key,
                {
                    "deskripsi": None,
                    "foto_url": None,
                },
            )

            item["deskripsi"] = detail["deskripsi"]
            item["foto_url"] = detail["foto_url"]

        waktu_selesai = time.perf_counter()

        # ---------------------------------------------
        # 6. Log performa
        # ---------------------------------------------

        print(
            f"[PERFORMA] Rekomendasi selesai | "
            f"Query: {permintaan.query!r} | "
            f"Jumlah hasil: {hasil['jumlah_hasil']} | "
            f"Database: {waktu_database - waktu_mulai:.4f} detik | "
            f"Perhitungan dan detail: "
            f"{waktu_selesai - waktu_database:.4f} detik | "
            f"Total: {waktu_selesai - waktu_mulai:.4f} detik",
            flush=True,
        )

        # ---------------------------------------------
        # 7. Respons API
        # ---------------------------------------------

        return {
            "status": "success",
            **hasil,
        }

    except HTTPException:
        raise

    except SQLAlchemyError as error:
        print(
            f"[ERROR] Database rekomendasi: {error}",
            flush=True,
        )

        raise HTTPException(
            status_code=500,
            detail="Gagal mengambil data rekomendasi pantai.",
        )

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
            detail="Terjadi kesalahan saat memproses rekomendasi pantai.",
        )


# =========================================================
# 9. ENDPOINT KOORDINAT PANTAI
# =========================================================

@router.get("/koordinat")
def get_koordinat_pantai():
    query = text("""
        SELECT
            dp.pantai,
            dp.latitude,
            dp.longitude
        FROM public.data_pantai dp
        INNER JOIN public.pantai_master pm
            ON LOWER(TRIM(dp.pantai)) = LOWER(TRIM(pm.nama_pantai))
        ORDER BY dp.pantai ASC
    """)

    try:
        with engine.connect() as connection:
            hasil = connection.execute(
                query
            ).mappings().all()

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

    except SQLAlchemyError as error:
        print(
            f"[ERROR] Koordinat pantai: {error}",
            flush=True,
        )

        raise HTTPException(
            status_code=500,
            detail="Gagal mengambil koordinat pantai.",
        )
