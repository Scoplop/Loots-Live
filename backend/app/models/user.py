"""
Modèle User - Authentification et compte utilisateur.
"""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

from backend.app.database import Base


class User(Base):
    """Table des utilisateurs (comptes joueurs)"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relations
    villages: Mapped[List["Village"]] = relationship(
        "Village",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    characters: Mapped[List["Character"]] = relationship(
        "Character",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    chat_messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage",
        foreign_keys="[ChatMessage.user_id]",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"
