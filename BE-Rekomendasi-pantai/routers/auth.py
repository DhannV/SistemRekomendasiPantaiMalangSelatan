
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from database import engine
from security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
)
from schemas.auth import RegisterRequest, LoginRequest


# ==========================================
# KONFIGURASI
# ==========================================

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

bearer_scheme = HTTPBearer()

logger = logging.getLogger(__name__)


# ==========================================
# REGISTER
# ==========================================

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest):

    username = data.username.strip()

    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username tidak boleh kosong."
        )

    try:
        # Hash password sebelum disimpan
        hashed_password = hash_password(data.password)

        with engine.begin() as connection:

            # Periksa apakah username sudah digunakan
            existing_user = connection.execute(
                text("""
                    SELECT id
                    FROM public.users
                    WHERE username = :username
                    LIMIT 1
                """),
                {"username": username}
            ).first()

            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username sudah digunakan."
                )

            # Simpan pengguna baru
            result = connection.execute(
                text("""
                    INSERT INTO public.users (
                        username,
                        hashed_password,
                        role
                    )
                    VALUES (
                        :username,
                        :hashed_password,
                        'user'
                    )
                    RETURNING id, username, role, created_at
                """),
                {
                    "username": username,
                    "hashed_password": hashed_password
                }
            )

            user = result.mappings().one()

        logger.info("Registrasi berhasil untuk username: %s", username)

        return {
            "message": "Registrasi berhasil.",
            "user": dict(user)
        }

    except HTTPException:
        raise

    except IntegrityError:
        logger.exception(
            "REGISTER ERROR: Terjadi pelanggaran constraint database."
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username sudah digunakan atau data tidak valid."
        )

    except SQLAlchemyError:
        logger.exception(
            "REGISTER ERROR: Gagal menyimpan akun ke database."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan saat menyimpan akun."
        )

    except Exception:
        logger.exception(
            "REGISTER ERROR: Terjadi kesalahan tidak terduga."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan pada server."
        )


# ==========================================
# LOGIN
# ==========================================

@router.post("/login")
def login(data: LoginRequest):

    username = data.username.strip()

    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username tidak boleh kosong."
        )

    try:
        with engine.connect() as connection:

            result = connection.execute(
                text("""
                    SELECT id, username, hashed_password, role
                    FROM public.users
                    WHERE username = :username
                    LIMIT 1
                """),
                {"username": username}
            )

            user = result.mappings().first()

    except SQLAlchemyError:
        logger.exception("LOGIN ERROR: Gagal mengakses database.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengakses database."
        )

    if not user or not verify_password(
        data.password,
        user["hashed_password"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah."
        )

    try:
        token = create_access_token(user["id"])

    except Exception:
        logger.exception("LOGIN ERROR: Gagal membuat access token.")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal membuat token autentikasi."
        )

    logger.info("Login berhasil untuk username: %s", username)

    return {
        "message": "Login berhasil.",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"]
        }
    }


# ==========================================
# AUTENTIKASI: MENGAMBIL PENGGUNA DARI TOKEN
# ==========================================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):

    token = credentials.credentials

    try:
        user_id = verify_access_token(token)

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau sudah kedaluwarsa.",
            headers={"WWW-Authenticate": "Bearer"}
        )

    try:
        with engine.connect() as connection:

            result = connection.execute(
                text("""
                    SELECT id, username, role, created_at
                    FROM public.users
                    WHERE id = :user_id
                    LIMIT 1
                """),
                {"user_id": user_id}
            )

            user = result.mappings().first()

    except SQLAlchemyError:
        logger.exception(
            "AUTH ERROR: Gagal mengambil data pengguna dari database."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengakses database."
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Pengguna tidak ditemukan."
        )

    return dict(user)


# ==========================================
# OTORISASI: KHUSUS ADMIN
# ==========================================

def require_admin(
    current_user: dict = Depends(get_current_user)
):

    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Khusus Admin."
        )

    return current_user


# ==========================================
# PROFIL PENGGUNA YANG SEDANG LOGIN
# ==========================================

@router.get("/me")
def get_me(
    current_user: dict = Depends(get_current_user)
):

    return {
        "user": current_user
    }


# ==========================================
# ENDPOINT UJI COBA AKSES ADMIN
# ==========================================

@router.get("/admin-test")
def admin_test(
    current_user: dict = Depends(require_admin)
):

    return {
        "message": "Akses Admin berhasil.",
        "user": current_user
    }
