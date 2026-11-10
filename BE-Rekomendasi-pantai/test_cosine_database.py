
from sqlalchemy import text

from database import engine
from services.profil_pantai import bangun_semua_profil
from services.tfidf_manual import bangun_semua_vektor_tfidf
from services.cosine_similarity import (
    hitung_cosine_similarity,
    hitung_semua_cosine,
)


# 1. Ambil ulasan dari Supabase
with engine.connect() as connection:
    rows = connection.execute(text("""
        SELECT pantai, teks
        FROM public.dataset_pantai
        WHERE pantai IS NOT NULL
          AND TRIM(pantai) <> ''
          AND teks IS NOT NULL
          AND TRIM(teks) <> ''
    """)).mappings().all()

data = [dict(row) for row in rows]


# 2. Bentuk profil pantai
profil = bangun_semua_profil(data)


# 3. Bentuk vektor TF-IDF
hasil_tfidf = bangun_semua_vektor_tfidf(
    profil["istilah_pantai"]
)

vektor_pantai = hasil_tfidf["vektor_pantai"]


# 4. Hitung cosine similarity
matriks_cosine = hitung_semua_cosine(vektor_pantai)

print("Jumlah pantai:", len(vektor_pantai))
print("Jumlah kosakata:", len(hasil_tfidf["kosakata"]))

# 5. Uji satu pantai terhadap dirinya sendiri
pantai_uji = "Pantai Balekambang"

if pantai_uji in vektor_pantai:
    skor_diri_sendiri = hitung_cosine_similarity(
        vektor_pantai[pantai_uji],
        vektor_pantai[pantai_uji],
    )
    print(
        f"Cosine {pantai_uji} terhadap dirinya sendiri:",
        round(skor_diri_sendiri, 4),
    )

# 6. Tampilkan 5 pantai paling mirip dengan Pantai Balekambang
if pantai_uji in matriks_cosine:
    hasil_urut = sorted(
        [
            (nama, skor)
            for nama, skor in matriks_cosine[pantai_uji].items()
            if nama != pantai_uji
        ],
        key=lambda item: item[1],
        reverse=True,
    )

    print(f"\n5 pantai paling mirip dengan {pantai_uji}:")
    for nama, skor in hasil_urut[:5]:
        print(f"{nama}: {skor:.4f}")
