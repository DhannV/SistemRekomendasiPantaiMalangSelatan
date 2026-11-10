import os
from dotenv import load_dotenv

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL tidak ditemukan. Periksa konfigurasi file .env."
    )

# Koneksi ke Supabase PostgreSQL
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

# Base untuk model SQLAlchemy
Base = declarative_base()

# Session database
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    try:
        with engine.connect() as connection:
            version = connection.execute(
                text("SELECT version()")
            ).scalar()

        print("[DATABASE] Koneksi berhasil.", flush=True)
        return version

    except SQLAlchemyError:
        import traceback

        print("[DATABASE] Koneksi gagal. Detail error:", flush=True)
        traceback.print_exc()
        raise