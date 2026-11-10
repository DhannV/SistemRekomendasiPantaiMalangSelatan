from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    Integer,
    Text,
    func,
)

from database import Base


class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(
        BigInteger,
        primary_key=True,
        index=True,
    )

    user_id = Column(
        BigInteger,
        nullable=False,
        index=True,
    )

    keyword = Column(
        Text,
        nullable=False,
    )

    result_count = Column(
        Integer,
        nullable=False,
        default=0,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            "length(trim(keyword)) > 0",
            name="search_history_keyword_not_empty",
        ),
        CheckConstraint(
            "result_count >= 0",
            name="search_history_result_count_nonnegative",
        ),
    )