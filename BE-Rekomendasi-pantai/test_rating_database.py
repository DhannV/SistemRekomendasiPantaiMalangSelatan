
from sqlalchemy import text

from database import engine
from services.rating_aggregation import hitung_bwr


# Ambil pantai dan rating dari Supabase
with engine.connect() as connection:
    rows = connection.execute(text("""
        SELECT pantai, rating
        FROM public.dataset_pantai
        WHERE pantai IS NOT NULL
          AND TRIM(pantai) <> ''
          AND rating IS NOT NULL
    """)).mappings().all()

data_rating = [dict(row) for row in rows]

print("Jumlah data rating:", len(data_rating))


# Hitung BWR
hasil = hitung_bwr(data_rating)

print("Jumlah pantai yang memiliki rating:", len(hasil["skor_bwr"]))
print("Rata-rata rating global:", round(hasil["rata_rata_global"], 4))
print("Nilai m (kuantil 0.6):", round(hasil["nilai_m"], 4))


# Tampilkan 5 pantai dengan BWR tertinggi
peringkat = sorted(
    hasil["skor_bwr"].items(),
    key=lambda item: item[1],
    reverse=True,
)

print("\n5 pantai dengan BWR tertinggi:")

for pantai, skor in peringkat[:5]:
    skor_normal = hasil["skor_bwr_normalisasi"][pantai]

    print(
        f"{pantai}: BWR={skor:.4f}, "
        f"Normalisasi={skor_normal:.4f}"
    )
