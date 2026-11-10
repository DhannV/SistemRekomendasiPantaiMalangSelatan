
from collections import Counter

from sqlalchemy import text

from database import engine
from services.rekomendasi import rekomendasikan_pantai
from services.preprocessing import proses_akhir
from services.profil_pantai import (
    bangun_semua_profil,
    ambil_istilah,
)
from services.tfidf_manual import (
    bangun_semua_vektor_tfidf,
    buat_vektor_query,
)


# ============================================================
# 1. AMBIL DATA DARI SUPABASE
# ============================================================

print("=" * 70)
print("1. MENGAMBIL DATA DARI SUPABASE")
print("=" * 70)

with engine.connect() as connection:
    rows_ulasan = connection.execute(
        text("""
            SELECT pantai, teks
            FROM public.dataset_pantai
            WHERE pantai IS NOT NULL
              AND TRIM(pantai) <> ''
              AND teks IS NOT NULL
              AND TRIM(teks) <> ''
        """)
    ).mappings().all()

    rows_rating = connection.execute(
        text("""
            SELECT pantai, rating
            FROM public.dataset_pantai
            WHERE pantai IS NOT NULL
              AND TRIM(pantai) <> ''
              AND rating IS NOT NULL
        """)
    ).mappings().all()

data_ulasan = [dict(row) for row in rows_ulasan]
data_rating = [dict(row) for row in rows_rating]

print(f"Jumlah ulasan       : {len(data_ulasan)}")
print(f"Jumlah data rating  : {len(data_rating)}")
print(
    "Jumlah pantai      :",
    len({row["pantai"] for row in data_ulasan})
)


# ============================================================
# 2. BANGUN PROFIL PANTAI DAN TF-IDF
# ============================================================

print("\n" + "=" * 70)
print("2. MEMBANGUN PROFIL PANTAI DAN TF-IDF")
print("=" * 70)

profil = bangun_semua_profil(data_ulasan)

tfidf = bangun_semua_vektor_tfidf(
    profil["istilah_pantai"]
)

print("Jumlah pantai dalam profil :", len(profil["daftar_pantai"]))
print("Jumlah kosakata TF-IDF     :", len(tfidf["kosakata"]))
print("Jumlah vektor pantai       :", len(tfidf["vektor_pantai"]))


# ============================================================
# 3. UJI QUERY
# ============================================================

print("\n" + "=" * 70)
print("3. PREPROCESSING QUERY")
print("=" * 70)

query = (
    "gedung perkantoran di tengah kota"
)

query_final = proses_akhir(query)

# Buat unigram dan bigram secara otomatis.
istilah_query = ambil_istilah(query_final)

# Buat vektor query dengan kosakata dan IDF hasil pelatihan.
vektor_query = buat_vektor_query(
    query_final,
    tfidf["kosakata"],
    tfidf["idf"],
)

print("Query asli:")
print(query)

print("\nQuery setelah preprocessing:")
print(query_final)

print("\nIstilah unigram dan bigram:")
print(istilah_query)

print("\nJumlah istilah query :", len(istilah_query))
print("Fitur vektor query   :", len(vektor_query))


# ============================================================
# 4. DIAGNOSIS KOSAKATA TF-IDF
# ============================================================

print("\n" + "=" * 70)
print("4. DIAGNOSIS KOSAKATA TF-IDF")
print("=" * 70)

df_semua = Counter()
frekuensi_total = Counter()

for daftar_istilah in profil["istilah_pantai"].values():
    df_semua.update(set(daftar_istilah))
    frekuensi_total.update(daftar_istilah)

jumlah_pantai = len(profil["istilah_pantai"])

# Ambil parameter dari modul TF-IDF agar diagnosis tidak
# menggunakan batas yang berbeda dari konfigurasi sebenarnya.
from services import tfidf_manual

min_df = tfidf_manual.MIN_DF
max_df = tfidf_manual.MAX_DF
max_fitur = tfidf_manual.MAX_FITUR

batas_df_maks = (
    max_df * jumlah_pantai
    if isinstance(max_df, float) and max_df <= 1
    else max_df
)

print("Jumlah pantai       :", jumlah_pantai)
print("MIN_DF              :", min_df)
print("MAX_DF              :", max_df)
print("Batas maksimum DF   :", batas_df_maks)
print("MAX_FITUR           :", max_fitur)

print("\nRincian setiap istilah:")

kosakata_set = set(tfidf["kosakata"])

for istilah in istilah_query:
    df = df_semua.get(istilah, 0)
    frekuensi = frekuensi_total.get(istilah, 0)
    terpilih = istilah in kosakata_set

    if terpilih:
        alasan = "Masuk kosakata TF-IDF"
    elif df < min_df:
        alasan = "Tidak memenuhi MIN_DF"
    elif df > batas_df_maks:
        alasan = "Melewati MAX_DF"
    else:
        alasan = "Tidak masuk kosakata terpilih"

    print(
        f"- {istilah!r}: "
        f"DF={df}, "
        f"frekuensi={frekuensi}, "
        f"terpilih={terpilih}, "
        f"alasan={alasan}"
    )

istilah_masuk = [
    istilah for istilah in istilah_query
    if istilah in kosakata_set
]

print("\nIstilah query yang masuk kosakata:")
print(istilah_masuk)

print("Jumlah istilah yang masuk:", len(istilah_masuk))


# ============================================================
# 5. PERIKSA VEKTOR TF-IDF QUERY
# ============================================================

print("\n" + "=" * 70)
print("5. VEKTOR TF-IDF QUERY")
print("=" * 70)

if vektor_query:
    for istilah, bobot in sorted(
        vektor_query.items(),
        key=lambda item: item[1],
        reverse=True,
    ):
        print(f"{istilah:<25} {bobot:.6f}")
else:
    print("Vektor query kosong.")
    print(
        "Tidak ada istilah query yang cocok dengan "
        "kosakata TF-IDF terpilih."
    )


# ============================================================
# 6. PERIKSA KECocOKAN QUERY DENGAN PROFIL PANTAI
# ============================================================

print("\n" + "=" * 70)
print("6. KECocOKAN ISTILAH DENGAN PROFIL PANTAI")
print("=" * 70)

pantai_uji = [
    "Pantai Batu Bengkung",
    "Pantai Balekambang",
    "Pantai Goa Cina",
]

# Gunakan nama pantai yang benar-benar tersedia di profil.
nama_pantai_tersedia = {
    nama.casefold(): nama
    for nama in tfidf["vektor_pantai"]
}

for nama_uji in pantai_uji:
    pantai = nama_pantai_tersedia.get(nama_uji.casefold())

    if pantai is None:
        print(f"\n{nama_uji}: nama tidak ditemukan dalam profil.")
        continue

    vektor_pantai = tfidf["vektor_pantai"].get(pantai, {})
    irisan = set(vektor_query) & set(vektor_pantai)

    print(f"\n{pantai}")
    print("Jumlah fitur pantai       :", len(vektor_pantai))
    print("Jumlah fitur yang cocok   :", len(irisan))
    print("Istilah yang cocok        :", sorted(irisan))


# ============================================================
# 7. JALANKAN REKOMENDASI HYBRID
# ============================================================

print("\n" + "=" * 70)
print("7. HASIL REKOMENDASI HYBRID")
print("=" * 70)

hasil = rekomendasikan_pantai(
    query=query,
    data_ulasan=data_ulasan,
    data_rating=data_rating,
)

print("Query asli       :", hasil["query"])
print("Query bersih     :", hasil["query_bersih"])
print("Jumlah hasil     :", hasil["jumlah_hasil"])

print("\nDaftar rekomendasi:")

for nomor, item in enumerate(hasil["data"], start=1):
    print(
        f"{nomor}. {item['pantai']} | "
        f"Cosine={item['skor_cosine']:.4f} | "
        f"BWR={item['skor_bwr']:.4f} | "
        f"Hybrid={item['skor_akhir']:.4f}"
    )

print("\nPengujian selesai.")
