
import time

from services.preprocessing import proses_akhir
from services.profil_pantai import bangun_semua_profil
from services.tfidf_manual import (
    bangun_semua_vektor_tfidf,
    buat_vektor_query,
)
from services.cosine_similarity import hitung_cosine_similarity
from services.rating_aggregation import hitung_bwr


ALPHA = 0.6
TOP_N = 5

# Cache model di memori backend
_MODEL_CACHE = None


def model_sudah_disiapkan():
    """Memeriksa apakah model sudah tersedia di memori."""
    return _MODEL_CACHE is not None


def siapkan_model(data_ulasan, data_rating):
    global _MODEL_CACHE

    if _MODEL_CACHE is not None:
        return

    waktu_total = time.perf_counter()

    # 1. Pembentukan profil pantai
    mulai = time.perf_counter()
    profil = bangun_semua_profil(data_ulasan)
    waktu_profil = time.perf_counter() - mulai

    # 2. Pembentukan TF-IDF
    mulai = time.perf_counter()
    hasil_tfidf = bangun_semua_vektor_tfidf(
        profil["istilah_pantai"]
    )
    waktu_tfidf = time.perf_counter() - mulai

    # 3. Perhitungan Bayesian Weighted Rating
    mulai = time.perf_counter()
    hasil_rating = hitung_bwr(data_rating)
    waktu_bwr = time.perf_counter() - mulai

    # 4. Simpan model ke cache
    _MODEL_CACHE = {
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

    print(
        "Model rekomendasi berhasil disiapkan dan disimpan di memori.",
        flush=True,
    )


def rekomendasikan_pantai(
    query,
    data_ulasan=None,
    data_rating=None,
    top_n=TOP_N,
    alpha=ALPHA,
    gerbang=True,
    normalisasi_cosine=True,
):
    """
    Menghasilkan rekomendasi menggunakan cosine similarity dan BWR.

    Model dipersiapkan satu kali. Setiap pencarian berikutnya
    hanya memproses query dan menghitung skor rekomendasi.
    """

    if not query or not query.strip():
        raise ValueError("Kata kunci pencarian tidak boleh kosong.")

    if not 0 <= alpha <= 1:
        raise ValueError("Alpha harus berada di antara 0 dan 1.")

    if top_n < 0:
        raise ValueError("top_n tidak boleh negatif.")

    # Persiapan hanya dilakukan jika model belum tersedia
    if _MODEL_CACHE is None:
        if data_ulasan is None or data_rating is None:
            raise RuntimeError(
                "Model belum disiapkan. Jalankan siapkan_model() terlebih dahulu."
            )

        siapkan_model(data_ulasan, data_rating)

    model = _MODEL_CACHE

    vektor_pantai = model["vektor_pantai"]
    kosakata = model["kosakata"]
    idf = model["idf"]
    bwr_normal = model["skor_bwr"]

    # 1. Preprocessing query pengguna
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

    # 2. Buat vektor untuk query baru
    vektor_query = buat_vektor_query(
        query_final,
        kosakata,
        idf,
    )

    # 3. Hitung cosine similarity
    skor_cosine = {
        pantai: hitung_cosine_similarity(vektor_query, vektor)
        for pantai, vektor in vektor_pantai.items()
    }

    # 4. Periksa kecocokan teks
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

    # 5. Tentukan kandidat pantai
    if gerbang and ada_kecocokan_teks:
        kandidat = {
            pantai: skor
            for pantai, skor in skor_cosine.items()
            if skor > 0
        }
    else:
        kandidat = dict(skor_cosine)

    # 6. Normalisasi cosine relatif terhadap skor maksimum
    skor_maks = max(skor_cosine.values(), default=0.0)

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

    # 7. Hitung skor hybrid menggunakan BWR yang sudah tersimpan
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

    # 8. Urutkan berdasarkan skor hybrid
    hasil_akhir.sort(
        key=lambda item: (
            item["skor_akhir"],
            item["skor_bwr"],
            item["pantai"],
        ),
        reverse=True,
    )

    # 9. Ambil Top-N
    hasil_akhir = hasil_akhir[:top_n]

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
