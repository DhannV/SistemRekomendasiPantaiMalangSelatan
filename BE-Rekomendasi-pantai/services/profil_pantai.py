
from services.preprocessing import bersihkan_teks, proses_akhir


# ============================================================
# PARAMETER PROFIL PANTAI
# Disesuaikan dengan notebook Google Colab
# ============================================================

THRESHOLD_ATRIBUT = 0.15
BOBOT_TAG = 1
NGRAM_MAKS = 2

KAMUS_ATRIBUT_4A = {
    "Atraksi": {
        "pasir_putih": [
            "pasir putih",
            "pasir bersih",
            "pasir halus",
        ],
        "ombak_tenang": [
            "ombak tenang",
            "air tenang",
            "aman berenang",
        ],
        "pemandangan": [
            "pemandangan",
            "view",
            "indah",
            "cantik",
        ],
    },
    "Aksesibilitas": {
        "akses_jalan": [
            "akses jalan",
            "jalan rusak",
            "jalan bagus",
            "jalan sempit",
            "jalan menuju",
        ],
        "jarak_tempuh": [
            "dekat",
            "jauh",
            "perjalanan jauh",
        ],
    },
    "Amenitas": {
        "toilet": [
            "toilet",
            "kamar mandi",
            "wc",
        ],
        "warung_makan": [
            "warung",
            "kuliner",
            "makanan",
            "makan",
        ],
        "parkir": [
            "parkir",
            "lahan parkir",
        ],
    },
    "Ancillary": {
        "harga_tiket": [
            "tiket",
            "harga masuk",
            "biaya masuk",
            "murah",
            "mahal",
        ],
        "keramahan": [
            "ramah",
            "pelayanan baik",
            "petugas baik",
        ],
    },
}


# ============================================================
# PEMBENTUKAN ISTILAH
# Unigram + bigram sesuai notebook
# ============================================================

def ambil_istilah(teks, n_maks=NGRAM_MAKS):
    """
    Menghasilkan istilah kata tunggal dan frasa berurutan.
    Frasa dibuat per teks, tidak melintasi batas antarulasan.
    """
    kata = [
        k for k in teks.split()
        if len(k) > 1
    ]

    istilah = list(kata)

    for n in range(2, n_maks + 1):
        for i in range(len(kata) - n + 1):
            istilah.append(" ".join(kata[i:i + n]))

    return istilah


# ============================================================
# PELABELAN ATRIBUT 4A
# ============================================================

def mengandung_frasa(teks, frasa):
    """
    Memeriksa frasa utuh agar 'view' tidak cocok dengan 'review'.
    """
    return (" " + frasa + " ") in (" " + teks + " ")


def siapkan_ulasan(ulasan_teks):
    """
    Menyiapkan format ulasan dari Supabase.

    Setiap item minimal memiliki:
    {
        "pantai": nama pantai,
        "teks": isi ulasan
    }
    """
    hasil = []

    for ulasan in ulasan_teks:
        nama_pantai = str(ulasan.get("pantai") or "").strip()
        teks_asli = str(ulasan.get("teks") or "").strip()

        if not nama_pantai or not teks_asli:
            continue

        hasil.append({
            "pantai": nama_pantai,
            "teks": teks_asli,
            "teks_bersih": bersihkan_teks(teks_asli),
            "teks_final": proses_akhir(teks_asli),
        })

    return hasil


def hitung_proporsi_atribut(ulasan_teks, daftar_pantai):
    """
    Menghitung proporsi ulasan yang menyebut setiap atribut.
    Ulasan dikelompokkan berdasarkan pantai agar lebih efisien.
    """
    hasil = {}

    # Kelompokkan ulasan satu kali berdasarkan pantai
    ulasan_per_pantai = {
        pantai: [] for pantai in daftar_pantai
    }

    for ulasan in ulasan_teks:
        nama_pantai = ulasan["pantai"]

        if nama_pantai in ulasan_per_pantai:
            ulasan_per_pantai[nama_pantai].append(ulasan)

    # Hitung proporsi setiap atribut
    for pantai in daftar_pantai:
        ulasan_pantai = ulasan_per_pantai[pantai]
        total = len(ulasan_pantai)
        hasil[pantai] = {}

        for kategori, daftar_sub in KAMUS_ATRIBUT_4A.items():
            for nama_sub, kata_kunci in daftar_sub.items():
                jumlah = 0

                for ulasan in ulasan_pantai:
                    teks = ulasan["teks_bersih"]

                    if any(
                        mengandung_frasa(teks, kk)
                        for kk in kata_kunci
                    ):
                        jumlah += 1

                proporsi = jumlah / total if total else 0.0

                hasil[pantai][(kategori, nama_sub)] = proporsi

    return hasil


def tentukan_atribut_menonjol(
    proporsi_atribut,
    daftar_pantai,
    threshold=THRESHOLD_ATRIBUT,
):
    """
    Memilih atribut yang proporsinya memenuhi threshold.
    Diurutkan dari proporsi tertinggi.
    """
    hasil = {}

    for pantai in daftar_pantai:
        lolos = [
            (kategori, nama_sub, proporsi)
            for (kategori, nama_sub), proporsi
            in proporsi_atribut[pantai].items()
            if proporsi >= threshold
        ]

        lolos.sort(
            key=lambda item: item[2],
            reverse=True,
        )

        hasil[pantai] = lolos

    return hasil


# ============================================================
# PROFIL ISTILAH PER PANTAI
# ============================================================

def bangun_profil_istilah(
    ulasan_teks,
    daftar_pantai,
    atribut_menonjol,
    bobot_tag=BOBOT_TAG,
):
    """
    Membentuk profil istilah per pantai.
    Ulasan sudah dikelompokkan agar tidak dipindai berulang kali.
    """
    istilah_pantai = {}

    # Kelompokkan ulasan berdasarkan pantai satu kali
    ulasan_per_pantai = {
        pantai: [] for pantai in daftar_pantai
    }

    for ulasan in ulasan_teks:
        nama_pantai = ulasan["pantai"]

        if nama_pantai in ulasan_per_pantai:
            ulasan_per_pantai[nama_pantai].append(ulasan)

    for pantai in daftar_pantai:
        daftar_istilah = []

        # Istilah dari ulasan pantai
        for ulasan in ulasan_per_pantai[pantai]:
            daftar_istilah.extend(
                ambil_istilah(ulasan["teks_final"])
            )

        # Istilah dari atribut 4A yang menonjol
        for kategori, nama_sub, proporsi in atribut_menonjol[pantai]:
            teks_atribut = nama_sub.replace("_", " ")
            teks_atribut_final = proses_akhir(teks_atribut)

            istilah_tag = ambil_istilah(teks_atribut_final)

            daftar_istilah.extend(
                istilah_tag * bobot_tag
            )

        istilah_pantai[pantai] = daftar_istilah

    return istilah_pantai


# ============================================================
# FUNGSI UTAMA PEMBENTUKAN PROFIL
# ============================================================

def bangun_semua_profil(ulasan_dari_database):
    import time

    waktu_total = time.perf_counter()

    # 1. Preprocessing ulasan
    mulai = time.perf_counter()
    ulasan_teks = siapkan_ulasan(ulasan_dari_database)
    waktu_preprocessing = time.perf_counter() - mulai

    # 2. Daftar pantai
    mulai = time.perf_counter()
    daftar_pantai = sorted({
        ulasan["pantai"]
        for ulasan in ulasan_teks
    })
    waktu_daftar = time.perf_counter() - mulai

    # 3. Proporsi atribut
    mulai = time.perf_counter()
    proporsi_atribut = hitung_proporsi_atribut(
        ulasan_teks,
        daftar_pantai,
    )
    waktu_proporsi = time.perf_counter() - mulai

    # 4. Atribut menonjol
    mulai = time.perf_counter()
    atribut_menonjol = tentukan_atribut_menonjol(
        proporsi_atribut,
        daftar_pantai,
    )
    waktu_atribut = time.perf_counter() - mulai

    # 5. Profil istilah
    mulai = time.perf_counter()
    istilah_pantai = bangun_profil_istilah(
        ulasan_teks,
        daftar_pantai,
        atribut_menonjol,
    )
    waktu_profil_istilah = time.perf_counter() - mulai

    waktu_total = time.perf_counter() - waktu_total

    print(
        "[PERFORMA PROFIL] "
        f"Preprocessing: {waktu_preprocessing:.2f} detik | "
        f"Daftar pantai: {waktu_daftar:.2f} detik | "
        f"Proporsi atribut: {waktu_proporsi:.2f} detik | "
        f"Atribut menonjol: {waktu_atribut:.2f} detik | "
        f"Profil istilah: {waktu_profil_istilah:.2f} detik | "
        f"Total: {waktu_total:.2f} detik",
        flush=True,
    )

    return {
        "ulasan_teks": ulasan_teks,
        "daftar_pantai": daftar_pantai,
        "proporsi_atribut": proporsi_atribut,
        "atribut_menonjol": atribut_menonjol,
        "istilah_pantai": istilah_pantai,
    }
