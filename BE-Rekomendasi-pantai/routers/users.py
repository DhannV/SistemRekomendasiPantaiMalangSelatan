
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database import engine
from routers.auth import require_admin

router = APIRouter(prefix="/users", tags=["Users"])


# ==========================================
# MENAMPILKAN SEMUA AKUN
# ==========================================
@router.get("")
def get_all_users(
    admin: dict = Depends(require_admin),
):
    try:
        with engine.connect() as connection:
            result = connection.execute(
                text("""
                    SELECT id, username, role, created_at
                    FROM public.users
                    ORDER BY created_at DESC
                """)
            )

            users = [dict(row) for row in result.mappings().all()]

        return users

    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal mengambil data akun.",
        )


# ==========================================
# MENGUBAH ROLE AKUN
# ==========================================
@router.patch("/{user_id}/role")
def update_user_role(
    user_id: int,
    payload: dict,
    admin: dict = Depends(require_admin),
):
    new_role = payload.get("role")

    if new_role not in ["user", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Role harus user atau admin.",
        )

    # Mencegah admin mengubah role dirinya sendiri
    if user_id == admin["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role akun yang sedang digunakan tidak dapat diubah.",
        )

    try:
        with engine.begin() as connection:
            result = connection.execute(
                text("""
                    UPDATE public.users
                    SET role = :role
                    WHERE id = :user_id
                    RETURNING id, username, role, created_at
                """),
                {
                    "role": new_role,
                    "user_id": user_id,
                },
            )

            user = result.mappings().first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Akun tidak ditemukan.",
                )

        return {
            "message": "Role akun berhasil diperbarui.",
            "user": dict(user),
        }

    except HTTPException:
        raise
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal memperbarui role akun.",
        )


# ==========================================
# MENGHAPUS AKUN
# ==========================================
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    admin: dict = Depends(require_admin),
):
    # Mencegah admin menghapus akun yang sedang digunakan
    if user_id == admin["id"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Akun yang sedang digunakan tidak dapat dihapus.",
        )

    try:
        with engine.begin() as connection:
            result = connection.execute(
                text("""
                    DELETE FROM public.users
                    WHERE id = :user_id
                    RETURNING id, username
                """),
                {"user_id": user_id},
            )

            user = result.mappings().first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Akun tidak ditemukan.",
                )

        return {
            "message": "Akun berhasil dihapus.",
            "user": dict(user),
        }

    except HTTPException:
        raise
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal menghapus akun.",
        )
