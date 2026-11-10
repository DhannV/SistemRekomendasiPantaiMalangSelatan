
from services.profil_pantai import bangun_semua_profil
from services.tfidf_manual import bangun_semua_vektor_tfidf

data_contoh = [
    {
        "pantai": "Pantai Contoh",
        "teks": "Pasir putih dan pemandangan indah. Warung makan tersedia.",
    },
    {
        "pantai": "Pantai Contoh",
        "teks": "Pasir putih, pemandangan cantik dan warung makan.",
    },
    {
        "pantai": "Pantai Lain",
        "teks": "Pasir putih, ombak tenang dan parkir luas.",
    },
]

profil = bangun_semua_profil(data_contoh)
hasil = bangun_semua_vektor_tfidf(profil["istilah_pantai"])

print("Jumlah pantai:", hasil["jumlah_pantai"])
print("Jumlah kosakata:", len(hasil["kosakata"]))
print("Jumlah vektor:", len(hasil["vektor_pantai"]))

for pantai, vektor in hasil["vektor_pantai"].items():
    print(f"\n{pantai}")
    print("Jumlah bobot:", len(vektor))
    print("Contoh:", list(vektor.items())[:5])
