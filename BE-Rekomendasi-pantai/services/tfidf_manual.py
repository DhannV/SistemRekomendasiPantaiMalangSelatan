
import math
from collections import Counter
from services.profil_pantai import ambil_istilah


# Parameter sesuai notebook Colab
MIN_DF = 2
MAX_DF = 0.6
MAX_FITUR = 1000
SUBLINEAR_TF = True


def bangun_kosakata(
    istilah_pantai,
    min_df=MIN_DF,
    max_df=MAX_DF,
    max_fitur=MAX_FITUR,
):
    """
    Memilih kosakata berdasarkan document frequency (DF).

    istilah_pantai:
        Dictionary {nama_pantai: list_istilah}
    """
    jumlah_pantai = len(istilah_pantai)

    if jumlah_pantai == 0:
        return [], {}, {}

    frekuensi_dokumen = Counter()
    frekuensi_total = Counter()

    for daftar_istilah in istilah_pantai.values():
        istilah_unik = set(daftar_istilah)

        for istilah in istilah_unik:
            frekuensi_dokumen[istilah] += 1

        frekuensi_total.update(daftar_istilah)

    batas_df_maks = max_df * jumlah_pantai

    kandidat = [
        istilah
        for istilah, df in frekuensi_dokumen.items()
        if df >= min_df and df <= batas_df_maks
    ]

    # Jika fitur melebihi batas, prioritaskan total kemunculan tertinggi.
    kandidat.sort(
        key=lambda istilah: frekuensi_total[istilah],
        reverse=True,
    )

    kosakata = kandidat[:max_fitur]

    df_terpilih = {
        istilah: frekuensi_dokumen[istilah]
        for istilah in kosakata
    }

    frekuensi_terpilih = {
        istilah: frekuensi_total[istilah]
        for istilah in kosakata
    }

    return kosakata, df_terpilih, frekuensi_terpilih


def hitung_idf(kosakata, df_terpilih, jumlah_pantai):
    """
    IDF = ln((1 + N) / (1 + df)) + 1
    """
    idf = {}

    for istilah in kosakata:
        df = df_terpilih[istilah]
        idf[istilah] = math.log(
            (1 + jumlah_pantai) / (1 + df)
        ) + 1

    return idf


def hitung_tf_idf_dokumen(
    daftar_istilah,
    kosakata_set,
    idf,
    sublinear_tf=SUBLINEAR_TF,
):
    """
    Menghitung bobot TF-IDF untuk satu dokumen pantai.
    """
    frekuensi = Counter(daftar_istilah)
    vektor = {}

    for istilah, jumlah in frekuensi.items():
        if istilah not in kosakata_set:
            continue

        if sublinear_tf:
            tf = 1 + math.log(jumlah)
        else:
            tf = jumlah

        bobot = tf * idf[istilah]

        if bobot != 0:
            vektor[istilah] = bobot

    return vektor


def bangun_semua_vektor_tfidf(istilah_pantai):
    """
    Fungsi utama TF-IDF manual.

    Menghasilkan kosakata, DF, IDF, frekuensi istilah,
    dan vektor TF-IDF untuk setiap pantai.
    """
    jumlah_pantai = len(istilah_pantai)

    kosakata, df_terpilih, frekuensi_terpilih = bangun_kosakata(
        istilah_pantai
    )

    idf = hitung_idf(
        kosakata,
        df_terpilih,
        jumlah_pantai,
    )

    kosakata_set = set(kosakata)
    vektor_pantai = {}

    for pantai, daftar_istilah in istilah_pantai.items():
        vektor_pantai[pantai] = hitung_tf_idf_dokumen(
            daftar_istilah,
            kosakata_set,
            idf,
        )

    return {
        "jumlah_pantai": jumlah_pantai,
        "kosakata": kosakata,
        "df": df_terpilih,
        "idf": idf,
        "frekuensi_total": frekuensi_terpilih,
        "vektor_pantai": vektor_pantai,
    }

def buat_vektor_query(teks_query, kosakata, idf):
    """
    Membuat vektor TF-IDF untuk teks pencarian
    menggunakan kosakata dan IDF dari profil pantai.
    """
    istilah_query = ambil_istilah(teks_query)

    return hitung_tf_idf_dokumen(
        istilah_query,
        set(kosakata),
        idf,
    )