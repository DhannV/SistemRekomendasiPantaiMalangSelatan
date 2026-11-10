
import re
from functools import lru_cache

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import (
    StopWordRemoverFactory,
)


# =========================================================
# 1. KONFIGURASI PREPROCESSING
# =========================================================

KATA_NEGASI = ["tidak", "bukan", "kurang", "belum"]

FRASA_DIHAPUS = ["kurang lebih"]

KAMUS_KATA_BAKU = {
    "bgt": "banget",
    "yg": "yang",
    "gk": "tidak",
    "ga": "tidak",
    "tp": "tapi",
    "bgus": "bagus",
    "dgn": "dengan",
    "utk": "untuk",
    "krn": "karena",
    "jg": "juga",
    "tmpt": "tempat",
    "bersi": "bersih",
    "rame": "ramai",
    "jln": "jalan",
    "gaada": "tidak ada",
    "gada": "tidak ada",
    "ndak": "tidak",
    "gak": "tidak",
    "nggak": "tidak",
    "bgtt": "banget",
    "kl": "kalau",
    "dn": "dan",
    "kudu": "harus",
    "pol": "banget",
    "poll": "banget",
}

STOPWORD_TAMBAHAN = {
    "nya", "pantai", "malang", "tempat", "banget", "sangat",
    "buat", "jadi", "sini", "kalau", "lebih", "cukup", "sih",
    "deh", "nih", "aja", "udah", "kok", "k", "kesini", "tuju",
    "kan", "dri", "aq", "in", "uni", "trus", "gaes", "next",
    "jasa", "ban", "the", "tau", "mana", "tepat", "asal",
    "masing", "tiap", "bila", "apabila", "kemudian",
}

STOPWORD_NAMA_TEMPAT = set()


# =========================================================
# 2. INISIALISASI STEMMER DAN STOPWORD
# =========================================================

stemmer = StemmerFactory().create_stemmer()

stopword_factory = StopWordRemoverFactory()

DAFTAR_STOPWORD = (
    set(stopword_factory.get_stop_words())
    | STOPWORD_TAMBAHAN
    | STOPWORD_NAMA_TEMPAT
)


# =========================================================
# 3. POLA REGEX
# =========================================================

POLA_URL = re.compile(r"http\S+")

POLA_KARAKTER_NON_LATIN = re.compile(r"[^\x00-\x7F]+")

POLA_HURUF_BERULANG = re.compile(r"(.)\1{2,}")

POLA_KARAKTER_TIDAK_VALID = re.compile(r"[^a-z\s]+")

POLA_SPASI = re.compile(r"\s+")

POLA_NEGASI = re.compile(
    r"\b(" + "|".join(map(re.escape, KATA_NEGASI)) + r")\s+([a-z]+)"
)


# =========================================================
# 4. PEMBERSIHAN TEKS
# =========================================================

def bersihkan_teks(teks):
    """
    Membersihkan teks dari URL, karakter khusus,
    angka, simbol, dan spasi berlebihan.
    """

    teks = str(teks or "").lower()

    teks = POLA_URL.sub(" ", teks)

    teks = POLA_KARAKTER_NON_LATIN.sub(" ", teks)

    teks = POLA_HURUF_BERULANG.sub(r"\1", teks)

    teks = POLA_KARAKTER_TIDAK_VALID.sub(" ", teks)

    teks = POLA_SPASI.sub(" ", teks).strip()

    return teks


# =========================================================
# 5. NORMALISASI KATA
# =========================================================

def perbaiki_kata_baku(teks):
    """
    Mengubah kata tidak baku menjadi kata baku
    berdasarkan kamus yang telah ditentukan.
    """

    hasil = []

    for kata in teks.split():
        pengganti = KAMUS_KATA_BAKU.get(kata, kata)
        hasil.extend(pengganti.split())

    return " ".join(hasil)


def hapus_frasa_bukan_negasi(teks):
    """
    Menghapus frasa tertentu tanpa menghilangkan
    kata negasi yang memiliki makna penting.
    """

    for frasa in FRASA_DIHAPUS:
        teks = teks.replace(frasa, " ")

    return POLA_SPASI.sub(" ", teks).strip()


# =========================================================
# 6. STEMMING
# =========================================================

@lru_cache(maxsize=10000)
def stem_kata(kata):
    """
    Mengubah kata menjadi bentuk dasarnya.
    Menggunakan cache agar kata yang sama tidak
    perlu diproses ulang oleh Sastrawi.
    """

    if "_" in kata:
        awalan, inti = kata.split("_", 1)
        return awalan + "_" + stem_kata(inti)

    return stemmer.stem(kata)


# =========================================================
# 7. PREPROCESSING AKHIR
# =========================================================

def proses_akhir(teks_mentah):
    """
    Tahapan preprocessing:
    1. Cleaning
    2. Normalisasi kata
    3. Penghapusan frasa tertentu
    4. Penandaan kata negasi
    5. Stopword removal
    6. Stemming
    7. Stopword removal ulang
    """

    # 1. Cleaning
    teks = bersihkan_teks(teks_mentah)

    # 2. Normalisasi kata tidak baku
    teks = perbaiki_kata_baku(teks)

    # 3. Menghapus frasa tertentu
    teks = hapus_frasa_bukan_negasi(teks)

    # 4. Menjaga makna kata negasi
    teks = POLA_NEGASI.sub(r"\1_\2", teks)

    # 5. Stopword removal sebelum stemming
    kata_kata = [
        kata
        for kata in teks.split()
        if kata not in DAFTAR_STOPWORD
    ]

    # 6. Stemming dengan cache
    kata_kata = [
        stem_kata(kata)
        for kata in kata_kata
    ]

    # 7. Stopword removal setelah stemming
    kata_kata = [
        kata
        for kata in kata_kata
        if kata not in DAFTAR_STOPWORD and len(kata) > 1
    ]

    return " ".join(kata_kata)
