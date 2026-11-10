from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from sqlalchemy.exc import SQLAlchemyError
import traceback
from database import get_db
from models.search_history import SearchHistory
from schemas.search_history import (
    SearchHistoryCreate,
    SearchHistoryResponse,
)
from routers.auth import get_current_user, require_admin

router = APIRouter(
    prefix="/search-history",
    tags=["Search History"],
)


# Menyimpan riwayat pencarian pengguna
@router.post(
    "",
    response_model=SearchHistoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_search_history(
    payload: SearchHistoryCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    keyword = payload.keyword.strip()

    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Kata kunci tidak boleh kosong.",
        )

    history = SearchHistory(
        user_id=current_user["id"],
        keyword=keyword,
        result_count=payload.result_count,
    )

    try:
        db.add(history)
        db.commit()
        db.refresh(history)
        return history

    except SQLAlchemyError as e:
        db.rollback()

        print("ERROR SIMPAN SEARCH HISTORY:", repr(e), flush=True)
        traceback.print_exc()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal menyimpan riwayat pencarian.",
        )


# Mengambil riwayat milik pengguna yang sedang login
@router.get(
    "",
    response_model=list[SearchHistoryResponse],
)
def get_my_search_history(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    return (
        db.query(SearchHistory)
        .filter(SearchHistory.user_id == current_user["id"])
        .order_by(desc(SearchHistory.created_at))
        .all()
    )


# Mengambil semua riwayat pencarian (admin)
@router.get(
    "/admin",
    response_model=list[SearchHistoryResponse],
)
def get_all_search_history(
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin),
):
    return (
        db.query(SearchHistory)
        .order_by(desc(SearchHistory.created_at))
        .all()
    )


# Mengambil kata kunci terpopuler (admin)
@router.get("/admin/popular-keywords")
def get_popular_keywords(
    db: Session = Depends(get_db),
    admin: dict = Depends(require_admin),
):
    results = (
        db.query(
            SearchHistory.keyword,
            func.count(SearchHistory.id).label("total_search"),
        )
        .group_by(SearchHistory.keyword)
        .order_by(func.count(SearchHistory.id).desc())
        .limit(10)
        .all()
    )

    return [
        {
            "keyword": row.keyword,
            "total_search": row.total_search,
        }
        for row in results
    ]