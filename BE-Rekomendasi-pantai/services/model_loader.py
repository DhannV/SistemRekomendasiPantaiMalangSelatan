
import time
from pathlib import Path

import joblib

from services.rekomendasi import (
    simpan_model_ke_memori,
    VERSI_MODEL,
)


# =========================================================
# 1. LOKASI FILE MODEL
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

LOKASI_MODEL = (
    BASE_DIR
    / "models"
    / "model_rekomendasi.joblib"
)


# =========================================================
# 2. MEMUAT MODEL JOBLIB
# =========================================================

def muat_model():
    """
    Membaca model rekomendasi dari file Joblib
    dan memasukkannya ke cache memori backend.

    Fungsi ini dipanggil ketika FastAPI startup.
    """

    waktu_mulai = time.perf_counter()

    print("[MODEL LOADER] Memulai pemuatan model...", flush=True)

    # -----------------------------------------------------
    # Memastikan file model tersedia
    # -----------------------------------------------------

    if not LOKASI_MODEL.exists():
        raise FileNotFoundError(
            f"File model tidak ditemukan: {LOKASI_MODEL}"
        )

    # -----------------------------------------------------
    # Membaca file Joblib
    # -----------------------------------------------------

    model = joblib.load(LOKASI_MODEL)

    if not isinstance(model, dict):
        raise TypeError(
            "Isi file Joblib bukan dictionary model."
        )

    # -----------------------------------------------------
    # Memeriksa versi model
    # -----------------------------------------------------

    versi_model = model.get("versi_model")

    if versi_model != VERSI_MODEL:
        raise ValueError(
            f"Versi model tidak sesuai. "
            f"Versi file: {versi_model}, "
            f"versi backend: {VERSI_MODEL}."
        )

    # -----------------------------------------------------
    # Memasukkan model ke cache memori
    # -----------------------------------------------------

    simpan_model_ke_memori(model)

    waktu_selesai = time.perf_counter() - waktu_mulai

    print(
        "[MODEL LOADER] Model berhasil dimuat | "
        f"Lokasi: {LOKASI_MODEL} | "
        f"Jumlah pantai: {len(model['vektor_pantai'])} | "
        f"Jumlah kosakata: {len(model['kosakata'])} | "
        f"Waktu: {waktu_selesai:.2f} detik",
        flush=True,
    )

    return model
