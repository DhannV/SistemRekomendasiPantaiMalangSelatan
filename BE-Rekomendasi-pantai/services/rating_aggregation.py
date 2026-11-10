
import math

KUANTIL_M = 0.6


def hitung_kuantil(data, q=KUANTIL_M):
    """
    Menghitung kuantil dengan interpolasi linear,
    menggunakan posisi q * (n - 1).
    """
    if not data:
        return 0.0

    data_urut = sorted(data)

    if len(data_urut) == 1:
        return float(data_urut[0])

    posisi = q * (len(data_urut) - 1)
    indeks_bawah = math.floor(posisi)
    indeks_atas = math.ceil(posisi)

    if indeks_bawah == indeks_atas:
        return float(data_urut[indeks_bawah])

    pecahan = posisi - indeks_bawah

    return (
        data_urut[indeks_bawah] * (1 - pecahan)
        + data_urut[indeks_atas] * pecahan
    )


def normalisasi_min_max(nilai):
    """
    Mengubah nilai menjadi rentang 0 sampai 1.
    """
    if not nilai:
        return {}

    nilai_min = min(nilai.values())
    nilai_max = max(nilai.values())

    if nilai_max == nilai_min:
        return {kunci: 0.0 for kunci in nilai}

    return {
        kunci: (skor - nilai_min) / (nilai_max - nilai_min)
        for kunci, skor in nilai.items()
    }


def hitung_bwr(data_rating, kuantil_m=KUANTIL_M):
    """
    Menghitung Bayesian Weighted Rating (BWR).

    Format data_rating:
    [
        {"pantai": "Pantai A", "rating": 4.5},
        {"pantai": "Pantai A", "rating": 5.0},
        ...
    ]
    """
    rating_per_pantai = {}

    # Kelompokkan rating berdasarkan pantai
    for baris in data_rating:
        pantai = str(baris.get("pantai") or "").strip()
        rating = baris.get("rating")

        if not pantai or rating is None:
            continue

        try:
            rating = float(rating)
        except (TypeError, ValueError):
            continue

        if not math.isfinite(rating):
            continue

        rating_per_pantai.setdefault(pantai, []).append(rating)

    # Hitung jumlah rating (v) dan rata-rata rating (R)
    statistik = {}

    for pantai, daftar_rating in rating_per_pantai.items():
        if not daftar_rating:
            continue

        statistik[pantai] = {
            "jumlah_rating": len(daftar_rating),
            "rata_rata_rating": (
                sum(daftar_rating) / len(daftar_rating)
            ),
        }

    if not statistik:
        return {
            "rata_rata_global": 0.0,
            "nilai_m": 0.0,
            "statistik": {},
            "skor_bwr": {},
            "skor_bwr_normalisasi": {},
        }

    # C = rata-rata dari rata-rata rating setiap pantai
    rata_rata_global = (
        sum(
            item["rata_rata_rating"]
            for item in statistik.values()
        )
        / len(statistik)
    )

    # m = kuantil jumlah ulasan setiap pantai
    jumlah_ulasan = [
        item["jumlah_rating"]
        for item in statistik.values()
    ]

    nilai_m = hitung_kuantil(jumlah_ulasan, kuantil_m)

    # BWR = (v / (v + m)) * R + (m / (v + m)) * C
    skor_bwr = {}

    for pantai, item in statistik.items():
        v = item["jumlah_rating"]
        r = item["rata_rata_rating"]
        penyebut = v + nilai_m

        if penyebut == 0:
            skor = rata_rata_global
        else:
            skor = (
                (v / penyebut) * r
                + (nilai_m / penyebut) * rata_rata_global
            )

        skor_bwr[pantai] = skor

    skor_normalisasi = normalisasi_min_max(skor_bwr)

    return {
        "rata_rata_global": rata_rata_global,
        "nilai_m": nilai_m,
        "statistik": statistik,
        "skor_bwr": skor_bwr,
        "skor_bwr_normalisasi": skor_normalisasi,
    }
