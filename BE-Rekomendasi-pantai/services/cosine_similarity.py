
import math


def hitung_norma(vektor):
    """
    Menghitung panjang atau norma vektor.
    """
    return math.sqrt(sum(bobot ** 2 for bobot in vektor.values()))


def hitung_cosine_similarity(vektor_a, vektor_b):
    """
    Menghitung cosine similarity secara manual
    menggunakan representasi vektor TF-IDF berbentuk dictionary.
    """
    if not vektor_a or not vektor_b:
        return 0.0

    # Hanya istilah yang sama pada kedua vektor
    istilah_bersama = set(vektor_a) & set(vektor_b)

    dot_product = sum(
        vektor_a[istilah] * vektor_b[istilah]
        for istilah in istilah_bersama
    )

    norma_a = hitung_norma(vektor_a)
    norma_b = hitung_norma(vektor_b)

    if norma_a == 0 or norma_b == 0:
        return 0.0

    similarity = dot_product / (norma_a * norma_b)

    # Mencegah nilai di luar rentang akibat pembulatan floating point
    return max(0.0, min(1.0, similarity))


def hitung_semua_cosine(vektor_pantai):
    """
    Menghitung cosine similarity untuk seluruh pasangan pantai.
    Hasilnya berupa matriks kemiripan.
    """
    daftar_pantai = list(vektor_pantai.keys())
    hasil = {}

    for pantai_a in daftar_pantai:
        hasil[pantai_a] = {}

        for pantai_b in daftar_pantai:
            hasil[pantai_a][pantai_b] = hitung_cosine_similarity(
                vektor_pantai[pantai_a],
                vektor_pantai[pantai_b]
            )

    return hasil
