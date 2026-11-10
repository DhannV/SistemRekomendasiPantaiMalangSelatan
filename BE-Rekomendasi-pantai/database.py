
import os
from dotenv import load_dotenv

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, declarative_base


# ==========================================
# KONFIGURASI ENVIRONMENT
# ==========================================

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL tidak ditemukan. "
        "Periksa Environment Variables di Render."
    )


# ==========================================
# KONEKSI DATABASE
# ==========================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=5,
    connect_args={
        "connect_timeout": 15
    }
)


# ==========================================
# BASE MODEL SQLALCHEMY
# ==========================================

Base = declarative_base()


# ==========================================
# SESSION DATABASE
# ==========================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ==========================================
# TEST KONEKSI DATABASE
# ==========================================

def test_connection():
    try:
        with engine.connect() as connection:

            version = connection.execute(
                text("SELECT version()")
            ).scalar()

        print(
            "[DATABASE] Koneksi berhasil.",
            flush=True
        )

        return version

    except SQLAlchemyError:
        import traceback

        print(
            "[DATABASE] Koneksi gagal. Detail error:",
            flush=True
        )

        traceback.print_exc()
        raise
