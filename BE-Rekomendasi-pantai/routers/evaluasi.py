
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from routers.auth import require_admin
from routers.pantai import pastikan_model_siap

from services.evaluasi import (
    ambil_semua_query,
    tambah_query,
    ubah_query,
    hapus_query,
    ambil_daftar_pantai,
    ambil_ground_truth,
    simpan_ground_truth,
    hapus_ground_truth,
    hitung_precision_at_k,
    hitung_recall_at_k,
    hitung_ndcg_at_k,
    KONFIGURASI_EVALUASI,
    K_EVALUASI,
)

from services.rekomendasi import rekomendasikan_pantai


# =====================================================
# ROUTER
# =====================================================

router = APIRouter(
    prefix="/evaluasi",
    tags=["Evaluasi"],
    dependencies=[Depends(require_admin)]
)


# =====================================================
# PYDANTIC SCHEMAS
# =====================================================

class QueryBaru(BaseModel):
    query_text: str = Field(min_length=1, max_length=200)


class QueryUpdate(BaseModel):
    query_text: str = Field(min_length=1, max_length=200)
    is_active: bool


class GroundTruthBaru(BaseModel):
    query_id: int
    beach_name: str = Field(min_length=1, max_length=255)
    relevance: int = Field(ge=0, le=3)


# =====================================================
# HELPER: NORMALISASI HASIL REKOMENDASI
# =====================================================

def normalisasi_hasil_rekomendasi(data):
    """
    Memastikan hasil rekomendasi berbentuk list
    dictionary yang memiliki key 'pantai'.
    """

    if isinstance(data, list):

        if not data:
            return []

        if all(
            isinstance(item, dict) and "pantai" in item
            for item in data
        ):
            return data

        raise ValueError(
            "Format list hasil rekomendasi tidak sesuai."
        )

    if isinstance(data, dict):

        if "pantai" in data:
            return [data]

        for value in data.values():

            if isinstance(value, list):
                try:
                    return normalisasi_hasil_rekomendasi(value)
                except ValueError:
                    continue

        raise ValueError(
            "Dictionary hasil rekomendasi tidak memiliki "
            "list rekomendasi yang dikenali."
        )

    raise ValueError(
        f"Tipe hasil rekomendasi tidak dikenali: {type(data).__name__}"
    )


# =====================================================
# HELPER: VALIDASI QUERY
# =====================================================

def validasi_query_text(query_text):
    """
    Memastikan query tidak kosong setelah spasi dihapus.
    """

    query_text = query_text.strip().lower()

    if not query_text:
        raise HTTPException(
            status_code=400,
            detail="Query tidak boleh kosong."
        )

    return query_text


# =====================================================
# QUERY PENGUJIAN
# =====================================================

@router.get("/queries")
def get_queries():

    try:
        data = ambil_semua_query()

        return {
            "status": "success",
            "data": data
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal mengambil query: {str(e)}"
        )


@router.post("/queries")
def post_query(permintaan: QueryBaru):

    query_text = validasi_query_text(permintaan.query_text)

    try:
        data = tambah_query(query_text)

        return {
            "status": "success",
            "message": "Query berhasil ditambahkan.",
            "data": data
        }

    except Exception as e:

        if "unique" in str(e).lower() or "duplicate" in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail="Query tersebut sudah tersedia."
            )

        raise HTTPException(
            status_code=500,
            detail=f"Gagal menambahkan query: {str(e)}"
        )


@router.put("/queries/{query_id}")
def put_query(query_id: int, permintaan: QueryUpdate):

    query_text = validasi_query_text(permintaan.query_text)

    try:
        data = ubah_query(
            query_id,
            query_text,
            permintaan.is_active
        )

        return {
            "status": "success",
            "message": "Query berhasil diperbarui.",
            "data": data
        }

    except ValueError as e:

        if "tidak ditemukan" in str(e).lower():
            raise HTTPException(
                status_code=404,
                detail=str(e)
            )

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal memperbarui query: {str(e)}"
        )


@router.delete("/queries/{query_id}")
def delete_query(query_id: int):

    try:
        hapus_query(query_id)

        return {
            "status": "success",
            "message": "Query berhasil dihapus."
        }

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal menghapus query: {str(e)}"
        )


# =====================================================
# DAFTAR PANTAI
# =====================================================

@router.get("/pantai")
def get_daftar_pantai():

    try:
        data = ambil_daftar_pantai()

        return {
            "status": "success",
            "data": data,
            "total": len(data)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal mengambil daftar pantai: {str(e)}"
        )


# =====================================================
# GROUND TRUTH
# =====================================================

@router.get("/ground-truth/{query_id}")
def get_ground_truth(query_id: int):

    try:
        data = ambil_ground_truth(query_id)

        return {
            "status": "success",
            "data": data,
            "total": len(data)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal mengambil Ground Truth: {str(e)}"
        )


@router.post("/ground-truth")
def post_ground_truth(permintaan: GroundTruthBaru):

    try:
        data = simpan_ground_truth(
            permintaan.query_id,
            permintaan.beach_name.strip(),
            permintaan.relevance
        )

        return {
            "status": "success",
            "message": "Ground Truth berhasil disimpan.",
            "data": data
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal menyimpan Ground Truth: {str(e)}"
        )


@router.delete("/ground-truth/{ground_truth_id}")
def delete_ground_truth(ground_truth_id: int):

    try:
        hapus_ground_truth(ground_truth_id)

        return {
            "status": "success",
            "message": "Ground Truth berhasil dihapus."
        }

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Gagal menghapus Ground Truth: {str(e)}"
        )


# =====================================================
# MENJALANKAN EVALUASI
# =====================================================

@router.post("/jalankan")
def jalankan_evaluasi():

    try:

        # ---------------------------------------------
        # 1. Pastikan model rekomendasi siap
        # ---------------------------------------------

        pastikan_model_siap()

        # ---------------------------------------------
        # 2. Ambil query aktif
        # ---------------------------------------------

        daftar_query = ambil_semua_query()

        query_aktif = [
            query
            for query in daftar_query
            if query["is_active"]
        ]

        if not query_aktif:
            raise HTTPException(
                status_code=400,
                detail="Belum ada query evaluasi yang aktif."
            )

        # ---------------------------------------------
        # 3. Ambil seluruh pantai dari dataset
        # ---------------------------------------------

        daftar_pantai = set(ambil_daftar_pantai())

        if not daftar_pantai:
            raise HTTPException(
                status_code=400,
                detail="Dataset belum memiliki daftar pantai."
            )

        # ---------------------------------------------
        # 4. Siapkan hasil seluruh metode
        # ---------------------------------------------

        hasil_semua_metode = []

        for konfigurasi in KONFIGURASI_EVALUASI:

            nama_metode = konfigurasi["nama"]
            alpha = konfigurasi["alpha"]
            gerbang = konfigurasi["gerbang"]

            hasil_per_query = []

            total_precision = 0
            total_recall = 0
            total_ndcg = 0

            jumlah_query_valid = 0

            # -----------------------------------------
            # 5. Evaluasi setiap query aktif
            # -----------------------------------------

            for query_data in query_aktif:

                query_id = query_data["id"]
                query_text = query_data["query_text"]

                # Ambil Ground Truth
                data_ground_truth = ambil_ground_truth(
                    query_id
                )

                ground_truth = {
                    item["beach_name"]: int(item["relevance"])
                    for item in data_ground_truth
                }

                pantai_sudah_dinilai = set(ground_truth.keys())

                pantai_belum_dinilai = (
                    daftar_pantai - pantai_sudah_dinilai
                )

                # -------------------------------------
                # 6. Validasi kelengkapan Ground Truth
                # -------------------------------------

                if pantai_belum_dinilai:

                    hasil_per_query.append({
                        "query_id": query_id,
                        "query": query_text,
                        "status": "belum_lengkap",
                        "jumlah_ground_truth": len(ground_truth),
                        "total_pantai": len(daftar_pantai),
                        "pantai_belum_dinilai": sorted(
                            pantai_belum_dinilai
                        ),
                        "pesan": (
                            f"Ground Truth belum lengkap. "
                            f"{len(ground_truth)} dari "
                            f"{len(daftar_pantai)} pantai sudah dinilai."
                        )
                    })

                    continue

                # -------------------------------------
                # 7. Validasi jumlah pantai relevan
                # -------------------------------------

                total_relevan = sum(
                    1
                    for nilai in ground_truth.values()
                    if nilai > 0
                )

                if total_relevan == 0:

                    hasil_per_query.append({
                        "query_id": query_id,
                        "query": query_text,
                        "status": "belum_lengkap",
                        "jumlah_ground_truth": len(ground_truth),
                        "total_pantai": len(daftar_pantai),
                        "pesan": (
                            "Tidak terdapat pantai dengan "
                            "relevansi lebih dari 0."
                        )
                    })

                    continue

                # -------------------------------------
                # 8. Jalankan algoritma rekomendasi
                # -------------------------------------

                hasil_asli = rekomendasikan_pantai(
                    query=query_text,
                    top_n=K_EVALUASI,
                    alpha=alpha,
                    gerbang=gerbang,
                    normalisasi_cosine=True
                )

                hasil_rekomendasi = normalisasi_hasil_rekomendasi(
                    hasil_asli
                )

                hasil_rekomendasi = hasil_rekomendasi[:K_EVALUASI]

                # -------------------------------------
                # 9. Hitung metrik evaluasi
                # -------------------------------------

                precision = hitung_precision_at_k(
                    hasil_rekomendasi,
                    ground_truth,
                    K_EVALUASI
                )

                recall = hitung_recall_at_k(
                    hasil_rekomendasi,
                    ground_truth,
                    K_EVALUASI
                )

                ndcg = hitung_ndcg_at_k(
                    hasil_rekomendasi,
                    ground_truth,
                    K_EVALUASI
                )

                # -------------------------------------
                # 10. Akumulasi nilai
                # -------------------------------------

                jumlah_query_valid += 1

                total_precision += precision
                total_recall += recall
                total_ndcg += ndcg

                hasil_per_query.append({
                    "query_id": query_id,
                    "query": query_text,
                    "status": "berhasil",

                    "precision_at_5": round(
                        precision, 4
                    ),

                    "recall_at_5": round(
                        recall, 4
                    ),

                    "ndcg_at_5": round(
                        ndcg, 4
                    ),

                    "rekomendasi": hasil_rekomendasi
                })

            # -----------------------------------------
            # 11. Hitung rata-rata setiap metode
            # -----------------------------------------

            if jumlah_query_valid > 0:

                rata_precision = (
                    total_precision / jumlah_query_valid
                )

                rata_recall = (
                    total_recall / jumlah_query_valid
                )

                rata_ndcg = (
                    total_ndcg / jumlah_query_valid
                )

            else:

                rata_precision = 0
                rata_recall = 0
                rata_ndcg = 0

            # -----------------------------------------
            # 12. Simpan hasil metode
            # -----------------------------------------

            hasil_semua_metode.append({

                "metode": nama_metode,

                "alpha": alpha,

                "gerbang": gerbang,

                "jumlah_query_aktif": len(query_aktif),

                "jumlah_query_valid": jumlah_query_valid,

                "precision_at_5": round(
                    rata_precision, 4
                ),

                "recall_at_5": round(
                    rata_recall, 4
                ),

                "ndcg_at_5": round(
                    rata_ndcg, 4
                ),

                "detail": hasil_per_query
            })

        # ---------------------------------------------
        # 13. Kembalikan hasil evaluasi
        # ---------------------------------------------

        return {
            "status": "success",

            "jumlah_query_aktif": len(query_aktif),

            "jumlah_pantai": len(daftar_pantai),

            "jumlah_metode": len(KONFIGURASI_EVALUASI),

            "hasil_evaluasi": hasil_semua_metode
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Gagal menjalankan evaluasi: {str(e)}"
        )
