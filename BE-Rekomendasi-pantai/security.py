import os
import jwt

from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

load_dotenv()

password_hash = PasswordHash.recommended()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password,
    )


def create_access_token(user_id: int) -> str:
    if not JWT_SECRET_KEY:
        raise RuntimeError(
            "JWT_SECRET_KEY belum dikonfigurasi."
        )

    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        ),
    }

    return jwt.encode(
        payload,
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def verify_access_token(token: str) -> int:
    if not JWT_SECRET_KEY:
        raise RuntimeError(
            "JWT_SECRET_KEY belum dikonfigurasi."
        )

    payload = jwt.decode(
        token,
        JWT_SECRET_KEY,
        algorithms=[JWT_ALGORITHM],
    )

    user_id = payload.get("sub")

    if not user_id:
        raise jwt.InvalidTokenError(
            "Token tidak memiliki user ID."
        )

    try:
        return int(user_id)
    except (ValueError, TypeError):
        raise jwt.InvalidTokenError(
            "User ID pada token tidak valid."
        )


def get_current_user(
    token: str = Depends(oauth2_scheme),
):
    from routers.auth import get_user_by_id

    try:
        user_id = verify_access_token(token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid atau sudah kedaluwarsa.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User tidak ditemukan.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user