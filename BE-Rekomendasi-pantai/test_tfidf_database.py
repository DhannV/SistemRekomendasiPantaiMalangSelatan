
from sqlalchemy import text
from database import engine
from services.profil_pantai import bangun_semua_profil
from services.tfidf_manual import bangun_semua_vektor_tfidf

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

print("Jumlah ulasan dari database:", len(data))
print("Jumlah pantai unik:", len(set(row["pantai"] for row in data)))

profil = bangun_semua_profil(data)
hasil = bangun_semua_vektor_tfidf(profil["istilah_pantai"])

print("Jumlah kosakata TF-IDF:", len(hasil["kosakata"]))

for pantai, vektor in hasil["vektor_pantai"].items():
    print(f"{pantai}: {len(vektor)} bobot TF-IDF")
