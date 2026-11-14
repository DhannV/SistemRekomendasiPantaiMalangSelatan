
import time

from services.preprocessing import proses_akhir
from services.tfidf_manual import (
    buat_vektor_query,
    bangun_semua_vektor_tfidf,
)
from services.profil_pantai import bangun_semua_profil
from services.cosine_similarity import hitung_cosine_similarity
from services.rating_aggregation import hitung_bwr


# =========================================================
# 1. KONFIGURASI REKOMENDASI
# =========================================================

ALPHA = 0.6
TOP_N = 5

VERSI_MODEL = 1

_MODEL_CACHE = None


# =========================================================
# 2. VALIDASI DAN CACHE MODEL
# =========================================================

def model_sudah_disiapkan():
    return _MODEL_CACHE is not None


def simpan_model_ke_memori(model):
    global _MODEL_CACHE

    if not isinstance(model, dict):
        raise TypeError(
            "Format model rekomendasi harus berupa dictionary."
        )

    kunci_wajib = {
        "vektor_pantai",
        "kosakata",
        "idf",
        "skor_bwr",
    }

    kunci_hilang = kunci_wajib - set(model.keys())

    if kunci_hilang:
        raise ValueError(
            f"Model tidak lengkap. Key yang hilang: {kunci_hilang}"
        )

    if not isinstance(model["vektor_pantai"], dict):
        raise TypeError("vektor_pantai harus berupa dictionary.")

    if not isinstance(model["kosakata"], list):
        raise TypeError("kosakata harus berupa list.")

    if not isinstance(model["idf"], dict):
        raise TypeError("idf harus berupa dictionary.")

    if not isinstance(model["skor_bwr"], dict):
        raise TypeError("skor_bwr harus berupa dictionary.")

    if not model["vektor_pantai"]:
        raise ValueError("Model tidak memiliki data vektor pantai.")

    _MODEL_CACHE = model

    print(
        "[MODEL] Model berhasil dimuat ke memori. "
        f"Jumlah pantai: {len(model['vektor_pantai'])}",
        flush=True,
    )


def hapus_model_dari_memori():
    global _MODEL_CACHE

    _MODEL_CACHE = None

    print("[MODEL] Cache model berhasil dikosongkan.", flush=True)


# =========================================================
# 3. PEMBENTUKAN MODEL
# =========================================================

def bangun_model(data_ulasan, data_rating):
    waktu_total = time.perf_counter()

    print("[MODEL] Memulai pembentukan model...", flush=True)

    mulai = time.perf_counter()

    profil = bangun_semua_profil(data_ulasan)

    waktu_profil = time.perf_counter() - mulai

    print(
        f"[MODEL] Profil pantai selesai: {waktu_profil:.2f} detik",
        flush=True,
    )

    mulai = time.perf_counter()

    hasil_tfidf = bangun_semua_vektor_tfidf(
        profil["istilah_pantai"]
    )

    waktu_tfidf = time.perf_counter() - mulai

    print(
        f"[MODEL] TF-IDF selesai: {waktu_tfidf:.2f} detik",
        flush=True,
    )

    mulai = time.perf_counter()

    hasil_rating = hitung_bwr(data_rating)

    waktu_bwr = time.perf_counter() - mulai

    print(
        f"[MODEL] BWR selesai: {waktu_bwr:.2f} detik",
        flush=True,
    )

    model = {
        "versi_model": VERSI_MODEL,
        "vektor_pantai": hasil_tfidf["vektor_pantai"],
        "kosakata": hasil_tfidf["kosakata"],
        "idf": hasil_tfidf["idf"],
        "skor_bwr": hasil_rating["skor_bwr_normalisasi"],
    }

    waktu_selesai = time.perf_counter() - waktu_total

    print(
        "[PERFORMA MODEL] "
        f"Profil pantai: {waktu_profil:.2f} detik | "
        f"TF-IDF: {waktu_tfidf:.2f} detik | "
        f"BWR: {waktu_bwr:.2f} detik | "
        f"Total: {waktu_selesai:.2f} detik",
        flush=True,
    )

    print("[MODEL] Pembentukan model berhasil.", flush=True)

    return model


# =========================================================
# 4. PROSES REKOMENDASI PANTAI
# =========================================================

def rekomendasikan_pantai(
    query,
    top_n=TOP_N,
    alpha=ALPHA,
    gerbang=True,
    normalisasi_cosine=True,
    daftar_pantai_aktif=None,
):
    """
    Menghasilkan rekomendasi Hybrid CBF dan Rating Aggregation.

    Kandidat rekomendasi dibatasi oleh daftar pantai aktif
    jika daftar_pantai_aktif diberikan.
    """

    # -----------------------------------------------------
    # 1. Validasi input
    # -----------------------------------------------------

    if not isinstance(query, str) or not query.strip():
        raise ValueError(
            "Kata kunci pencarian tidak boleh kosong."
        )

    if not 0 <= alpha <= 1:
        raise ValueError(
            "Alpha harus berada di antara 0 dan 1."
        )

    if top_n < 0:
        raise ValueError(
            "top_n tidak boleh negatif."
        )

    # -----------------------------------------------------
    # 2. Memastikan model tersedia
    # -----------------------------------------------------

    if not model_sudah_disiapkan():
        raise RuntimeError(
            "Model rekomendasi belum dimuat."
        )

    model = _MODEL_CACHE

    vektor_pantai = model["vektor_pantai"]
    kosakata = model["kosakata"]
    idf = model["idf"]
    bwr_normal = model["skor_bwr"]

    # -----------------------------------------------------
    # 3. Memfilter pantai aktif
    # -----------------------------------------------------

    if daftar_pantai_aktif is None:
        vektor_aktif = dict(vektor_pantai)

    else:
        nama_aktif = {
            str(nama).strip().casefold()
            for nama in daftar_pantai_aktif
            if nama and str(nama).strip()
        }

        vektor_aktif = {
            pantai: vektor
            for pantai, vektor in vektor_pantai.items()
            if pantai.strip().casefold() in nama_aktif
        }

    # Tidak ada pantai aktif yang cocok dengan model.
    if not vektor_aktif:
        return {
            "query": query,
            "query_bersih": proses_akhir(query),
            "jumlah_hasil": 0,
            "parameter": {
                "alpha": alpha,
                "bobot_cosine": alpha,
                "bobot_bwr": 1 - alpha,
                "top_n": top_n,
                "gerbang": gerbang,
                "normalisasi_cosine": normalisasi_cosine,
            },
            "peringatan": (
                "Belum ada pantai aktif yang tersedia di model rekomendasi."
            ),
            "data": [],
        }

    # -----------------------------------------------------
    # 4. Preprocessing query
    # -----------------------------------------------------

    query_final = proses_akhir(query)

    if not query_final:
        return {
            "query": query,
            "query_bersih": query_final,
            "jumlah_hasil": 0,
            "parameter": {
                "alpha": alpha,
                "bobot_cosine": alpha,
                "bobot_bwr": 1 - alpha,
                "top_n": top_n,
                "gerbang": gerbang,
                "normalisasi_cosine": normalisasi_cosine,
            },
            "peringatan": (
                "Query tidak menghasilkan teks setelah preprocessing."
            ),
            "data": [],
        }

    # -----------------------------------------------------
    # 5. Membuat vektor query TF-IDF
    # -----------------------------------------------------

    vektor_query = buat_vektor_query(
        query_final,
        kosakata,
        idf,
    )

    # -----------------------------------------------------
    # 6. Menghitung cosine similarity
    # -----------------------------------------------------

    skor_cosine = {
        pantai: hitung_cosine_similarity(
            vektor_query,
            vektor,
        )
        for pantai, vektor in vektor_aktif.items()
    }

    # -----------------------------------------------------
    # 7. Memeriksa kecocokan teks
    # -----------------------------------------------------

    ada_kecocokan_teks = (
        bool(vektor_query)
        and any(skor > 0 for skor in skor_cosine.values())
    )

    peringatan = None

    if not ada_kecocokan_teks:
        peringatan = (
            "Tidak ada istilah query yang cocok dengan kosakata TF-IDF. "
            "Hasil rekomendasi ditentukan berdasarkan rating."
        )

    # -----------------------------------------------------
    # 8. Menentukan kandidat
    # -----------------------------------------------------

    if gerbang and ada_kecocokan_teks:
        kandidat = {
            pantai: skor
            for pantai, skor in skor_cosine.items()
            if skor > 0
        }
    else:
        kandidat = dict(skor_cosine)

    # -----------------------------------------------------
    # 9. Normalisasi cosine similarity
    # -----------------------------------------------------

    skor_maks = max(
        skor_cosine.values(),
        default=0.0,
    )

    if normalisasi_cosine:
        if skor_maks > 0:
            cosine_normal = {
                pantai: skor / skor_maks
                for pantai, skor in kandidat.items()
            }
        else:
            cosine_normal = {
                pantai: 0.0
                for pantai in kandidat
            }
    else:
        cosine_normal = dict(kandidat)

    # -----------------------------------------------------
    # 10. Menghitung skor hybrid
    # -----------------------------------------------------

    hasil_akhir = []

    for pantai, skor_cos in cosine_normal.items():
        skor_rating = bwr_normal.get(pantai, 0.0)

        skor_hybrid = (
            alpha * skor_cos
            + (1 - alpha) * skor_rating
        )

        hasil_akhir.append({
            "pantai": pantai,
            "skor_cosine": round(skor_cos, 6),
            "skor_bwr": round(skor_rating, 6),
            "skor_akhir": round(skor_hybrid, 6),
        })

    # -----------------------------------------------------
    # 11. Mengurutkan hasil rekomendasi
    # -----------------------------------------------------

    hasil_akhir.sort(
        key=lambda item: (
            item["skor_akhir"],
            item["skor_bwr"],
            item["pantai"],
        ),
        reverse=True,
    )

    hasil_akhir = hasil_akhir[:top_n]

    # -----------------------------------------------------
    # 12. Menyusun respons
    # -----------------------------------------------------

    respons = {
        "query": query,
        "query_bersih": query_final,
        "jumlah_hasil": len(hasil_akhir),
        "parameter": {
            "alpha": alpha,
            "bobot_cosine": alpha,
            "bobot_bwr": 1 - alpha,
            "top_n": top_n,
            "gerbang": gerbang,
            "normalisasi_cosine": normalisasi_cosine,
        },
        "data": hasil_akhir,
    }

    if peringatan:
        respons["peringatan"] = peringatan

    return respons
