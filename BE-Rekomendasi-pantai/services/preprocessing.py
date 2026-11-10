
import re
from functools import lru_cache

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import (
    StopWordRemoverFactory,
)

# Konfigurasi mengikuti notebook Google Colab
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
BUANG_KATA_NAMA_PANTAI = False

stemmer = StemmerFactory().create_stemmer()

DAFTAR_STOPWORD = (
    set(StopWordRemoverFactory().get_stop_words())
    | STOPWORD_TAMBAHAN
    | STOPWORD_NAMA_TEMPAT
)

POLA_NEGASI = re.compile(
    r"\b(" + "|".join(map(re.escape, KATA_NEGASI)) + r")\s+([a-z]+)"
)


def bersihkan_teks(teks):
    teks = str(teks or "").lower()
    teks = re.sub(r"http\S+", "", teks)
    teks = re.sub(r"[^\x00-\x7F]+", " ", teks)
    teks = re.sub(r"(.)\1{2,}", r"\1", teks)
    teks = re.sub(r"[^a-z\s]", " ", teks)
    teks = re.sub(r"\s+", " ", teks).strip()
    return teks


def perbaiki_kata_baku(teks):
    hasil = []

    for kata in teks.split():
        pengganti = KAMUS_KATA_BAKU.get(kata, kata)
        hasil.extend(pengganti.split())

    return " ".join(hasil)


def hapus_frasa_bukan_negasi(teks):
    for frasa in FRASA_DIHAPUS:
        teks = teks.replace(frasa, " ")
    return teks


@lru_cache(maxsize=10000)
def stem_kata(kata):
    if "_" in kata:
        awalan, inti = kata.split("_", 1)
        return awalan + "_" + stem_kata(inti)

    return stemmer.stem(kata)


def proses_akhir(teks_mentah):
    """Preprocessing yang sama digunakan untuk ulasan dan query pengguna."""
    teks = bersihkan_teks(teks_mentah)
    teks = perbaiki_kata_baku(teks)
    teks = hapus_frasa_bukan_negasi(teks)
    teks = POLA_NEGASI.sub(r"\1_\2", teks)

    kata_kata = [
        kata for kata in teks.split()
        if kata not in DAFTAR_STOPWORD
    ]

    kata_kata = [stem_kata(kata) for kata in kata_kata]

    kata_kata = [
        kata for kata in kata_kata
        if kata not in DAFTAR_STOPWORD and len(kata) > 1
    ]

    return " ".join(kata_kata)
