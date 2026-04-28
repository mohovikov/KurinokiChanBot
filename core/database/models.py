from datetime import datetime
from typing import Optional
from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from core.database.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str] = mapped_column(String(128))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Связи
    memberships: Mapped[list["Membership"]] = relationship(
        back_populates="user",
        foreign_keys="Membership.user_id",
        primaryjoin="User.id == Membership.user_id",
    )
    marriages: Mapped[list["Membership"]] = relationship(
        back_populates="married_to",
        foreign_keys="Membership.married_to_id",
        primaryjoin="User.id == Membership.married_to_id",
    )
    proposals_to_me: Mapped[list["Membership"]] = relationship(
        back_populates="pending_proposal_to",
        foreign_keys="Membership.pending_proposal_to_id",
        primaryjoin="User.id == Membership.pending_proposal_to_id",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} telegram_id={self.telegram_id} username={self.username}>"


class Membership(Base):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("user_id", "group_id", name="uq_user_group"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    group_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)

    # Статистика
    hugs_given: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    hugs_receive: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    warns_count: Mapped[int] = mapped_column(Integer, server_default=text("0"))
    marriage_score: Mapped[int] = mapped_column(Integer, server_default=text("0"))

    # Брачные дела
    married_to_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, default=None
    )
    married_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, default=None
    )
    pending_proposal_to_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True, default=None
    )

    # Даты
    joined_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_activity: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Связи
    user: Mapped["User"] = relationship(
        back_populates="memberships",
        foreign_keys=[user_id],
        primaryjoin="User.id == Membership.user_id",
    )
    married_to: Mapped["User | None"] = relationship(
        back_populates="marriages",
        foreign_keys=[married_to_id],
        primaryjoin="User.id == Membership.married_to_id",
    )
    pending_proposal_to: Mapped["User | None"] = relationship(
        back_populates="proposals_to_me",
        foreign_keys=[pending_proposal_to_id],
        primaryjoin="User.id == Membership.pending_proposal_to_id",
    )

    def __repr__(self) -> str:
        return f"<Membership user_id={self.user_id} group_id={self.group_id}>"
