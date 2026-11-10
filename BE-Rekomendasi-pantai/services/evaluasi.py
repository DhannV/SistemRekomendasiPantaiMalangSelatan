
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database import engine

import math


# ==========================================
# QUERY PENGUJIAN
# ==========================================

def ambil_semua_query():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT
                id,
                query_text,
                is_active,
                created_at,
                updated_at
            FROM evaluation_queries
            ORDER BY id ASC
        """))

        return [dict(row._mapping) for row in result]


def tambah_query(query_text):
    query_text = query_text.strip().lower()

    if not query_text:
        raise ValueError("Query tidak boleh kosong.")

    with engine.begin() as conn:
        result = conn.execute(
            text("""
                INSERT INTO evaluation_queries (query_text)
                VALUES (:query_text)
                RETURNING id, query_text, is_active
            """),
            {"query_text": query_text}
        )

        return dict(result.fetchone()._mapping)


def ubah_query(query_id, query_text, is_active):
    query_text = query_text.strip().lower()

    if not query_text:
        raise ValueError("Query tidak boleh kosong.")

    with engine.begin() as conn:
        result = conn.execute(
            text("""
                UPDATE evaluation_queries
                SET
                    query_text = :query_text,
                    is_active = :is_active,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = :query_id
                RETURNING id, query_text, is_active
            """),
            {
                "query_id": query_id,
                "query_text": query_text,
                "is_active": is_active
            }
        )

        row = result.fetchone()

        if not row:
            raise ValueError("Query tidak ditemukan.")

        return dict(row._mapping)


def hapus_query(query_id):
    with engine.begin() as conn:
        result = conn.execute(
            text("""
                DELETE FROM evaluation_queries
                WHERE id = :query_id
                RETURNING id
            """),
            {"query_id": query_id}
        )

        if not result.fetchone():
            raise ValueError("Query tidak ditemukan.")

        return True


# ==========================================
# DAFTAR PANTAI
# ==========================================

def ambil_daftar_pantai():
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT DISTINCT pantai
            FROM dataset_pantai
            WHERE pantai IS NOT NULL
              AND TRIM(pantai) <> ''
            ORDER BY pantai ASC
        """))

        return [row[0] for row in result]


# ==========================================
# GROUND TRUTH
# ==========================================

def ambil_ground_truth(query_id):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT
                    id,
                    query_id,
                    beach_name,
                    relevance,
                    created_at,
                    updated_at
                FROM evaluation_ground_truth
                WHERE query_id = :query_id
                ORDER BY beach_name ASC
            """),
            {"query_id": query_id}
        )

        return [dict(row._mapping) for row in result]


def simpan_ground_truth(query_id, beach_name, relevance):
    if relevance not in [0, 1, 2, 3]:
        raise ValueError("Relevansi harus bernilai 0 sampai 3.")

    with engine.begin() as conn:

        # Pastikan query tersedia
        query = conn.execute(
            text("""
                SELECT id
                FROM evaluation_queries
                WHERE id = :query_id
            """),
            {"query_id": query_id}
        ).fetchone()

        if not query:
            raise ValueError("Query pengujian tidak ditemukan.")

        # Pastikan nama pantai berasal dari dataset
        pantai = conn.execute(
            text("""
                SELECT DISTINCT pantai
                FROM dataset_pantai
                WHERE pantai = :beach_name
            """),
            {"beach_name": beach_name}
        ).fetchone()

        if not pantai:
            raise ValueError(
                "Nama pantai tidak ditemukan di dataset_pantai."
            )

        result = conn.execute(
            text("""
                INSERT INTO evaluation_ground_truth (
                    query_id,
                    beach_name,
                    relevance
                )
                VALUES (
                    :query_id,
                    :beach_name,
                    :relevance
                )
                ON CONFLICT (query_id, beach_name)
                DO UPDATE SET
                    relevance = EXCLUDED.relevance,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING
                    id,
                    query_id,
                    beach_name,
                    relevance
            """),
            {
                "query_id": query_id,
                "beach_name": beach_name,
                "relevance": relevance
            }
        )

        return dict(result.fetchone()._mapping)


def hapus_ground_truth(ground_truth_id):
    with engine.begin() as conn:
        result = conn.execute(
            text("""
                DELETE FROM evaluation_ground_truth
                WHERE id = :ground_truth_id
                RETURNING id
            """),
            {"ground_truth_id": ground_truth_id}
        )

        if not result.fetchone():
            raise ValueError("Data Ground Truth tidak ditemukan.")

        return True


# ==========================================
# KONFIGURASI EVALUASI
# ==========================================

K_EVALUASI = 5

KONFIGURASI_EVALUASI = [
    {
        "nama": "CBF Only",
        "alpha": 1.0,
        "gerbang": True
    },
    {
        "nama": "Rating Only",
        "alpha": 0.0,
        "gerbang": False
    },
    {
        "nama": "Hybrid 60:40",
        "alpha": 0.6,
        "gerbang": True
    },
    {
        "nama": "Hybrid 70:30",
        "alpha": 0.7,
        "gerbang": True
    },
    {
        "nama": "Hybrid 80:20",
        "alpha": 0.8,
        "gerbang": True
    },
    {
        "nama": "Hybrid 90:10",
        "alpha": 0.9,
        "gerbang": True
    }
]


# ==========================================
# METRIK EVALUASI
# ==========================================

def hitung_precision_at_k(hasil_rekomendasi, ground_truth, k=5):
    relevan = 0

    for item in hasil_rekomendasi[:k]:
        nama_pantai = item["pantai"]

        if ground_truth.get(nama_pantai, 0) > 0:
            relevan += 1

    return relevan / k if k > 0 else 0


def hitung_recall_at_k(hasil_rekomendasi, ground_truth, k=5):
    total_relevan = sum(
        1 for nilai in ground_truth.values() if nilai > 0
    )

    if total_relevan == 0:
        return 0

    relevan_ditemukan = 0

    for item in hasil_rekomendasi[:k]:
        nama_pantai = item["pantai"]

        if ground_truth.get(nama_pantai, 0) > 0:
            relevan_ditemukan += 1

    return relevan_ditemukan / total_relevan


def hitung_ndcg_at_k(hasil_rekomendasi, ground_truth, k=5):
    dcg = 0

    for posisi, item in enumerate(hasil_rekomendasi[:k], start=1):
        nama_pantai = item["pantai"]
        relevance = ground_truth.get(nama_pantai, 0)

        gain = (2 ** relevance) - 1
        discount = math.log2(posisi + 1)

        dcg += gain / discount

    relevance_ideal = sorted(
        ground_truth.values(),
        reverse=True
    )[:k]

    idcg = 0

    for posisi, relevance in enumerate(relevance_ideal, start=1):
        gain = (2 ** relevance) - 1
        discount = math.log2(posisi + 1)

        idcg += gain / discount

    if idcg == 0:
        return 0

    return dcg / idcg
