
from services.profil_pantai import bangun_semua_profil

data_contoh = [
    {
        "pantai": "Pantai Contoh",
        "teks": "Pasir putih dan pasir bersih. Pemandangan indah.",
        "rating": 5,
    },
    {
        "pantai": "Pantai Contoh",
        "teks": "Pasir putih, pemandangan cantik dan warung makan.",
        "rating": 4,
    },
    {
        "pantai": "Pantai Lain",
        "teks": "Ombak tenang dan tempat parkir luas.",
        "rating": 4,
    },
]

hasil = bangun_semua_profil(data_contoh)

print("Jumlah pantai:", len(hasil["daftar_pantai"]))
print("\nDaftar pantai:", hasil["daftar_pantai"])

print("\nAtribut menonjol:")
for pantai, atribut in hasil["atribut_menonjol"].items():
    ringkas = [
        f"{kategori}-{nama} ({proporsi:.0%})"
        for kategori, nama, proporsi in atribut
    ]
    print(pantai, ":", ringkas or "(tidak ada)")

print("\nJumlah istilah per pantai:")
for pantai, istilah in hasil["istilah_pantai"].items():
    print(pantai, ":", len(istilah), "istilah")
    print("Contoh:", istilah[:15])
