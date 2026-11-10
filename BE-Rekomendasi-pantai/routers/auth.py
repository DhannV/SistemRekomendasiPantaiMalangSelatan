
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database import engine
from security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
)
from schemas.auth import RegisterRequest, LoginRequest


router = APIRouter(prefix="/auth", tags=["Authentication"])

bearer_scheme = HTTPBearer()


# ==========================================
# REGISTER
# ==========================================
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest):
    username = data.username.strip()

    try:
        with engine.begin() as connection:
            existing_user = connection.execute(
                text("""
                    SELECT id
                    FROM public.users
                    WHERE username = :username
                """),
                {"username": username},
            ).first()

            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Username sudah digunakan.",
                )

            hashed_password = hash_password(data.password)

            result = connection.execute(
                text("""
                    INSERT INTO public.users
                        (username, hashed_password, role)
                    VALUES
                        (:username, :hashed_password, 'user')
                    RETURNING id, username, role, created_at
                """),
                {
                    "username": username,
                    "hashed_password": hashed_password,
                },
            )

            user = result.mappings().one()

        return {
            "message": "Registrasi berhasil.",
            "user": dict(user),
        }

    except HTTPException:
        raise
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan saat menyimpan akun.",
        )


# ==========================================
# LOGIN
# ==========================================
@router.post("/login")
def login(data: LoginRequest):
    username = data.username.strip()

    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("""
                    SELECT id, username, hashed_password, role
                    FROM public.users
                    WHERE username = :username
                """),
                {"username": username},
            )

            user = result.mappings().first()

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengakses database.",
        )

    if not user or not verify_password(
        data.password,
        user["hashed_password"],
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Username atau password salah.",
        )

    token = create_access_token(user["id"])

    return {
        "message": "Login berhasil.",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "role": user["role"],
        },
    }


# ==========================================
# AUTENTIKASI: MENGAMBIL PENGGUNA DARI TOKEN
# ==========================================
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    token = credentials.credentials

    try:
        user_id = verify_access_token(token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau sudah kedaluwarsa.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("""
                    SELECT id, username, role, created_at
                    FROM public.users
                    WHERE id = :user_id
                """),
                {"user_id": user_id},
            )

            user = result.mappings().first()

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengakses database.",
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Pengguna tidak ditemukan.",
        )

    return dict(user)


# ==========================================
# OTORISASI: KHUSUS ADMIN
# ==========================================
def require_admin(
    current_user: dict = Depends(get_current_user),
):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Akses ditolak. Khusus Admin.",
        )

    return current_user


# ==========================================
# PROFIL PENGGUNA YANG SEDANG LOGIN
# ==========================================
@router.get("/me")
def get_me(
    current_user: dict = Depends(get_current_user),
):
    return {
        "user": current_user,
    }


# ==========================================
# ENDPOINT UJI COBA AKSES ADMIN
# ==========================================
@router.get("/admin-test")
def admin_test(
    current_user: dict = Depends(require_admin),
):
    return {
        "message": "Akses Admin berhasil.",
        "user": current_user,
    }
