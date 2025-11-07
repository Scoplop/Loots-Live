"""
Modèle Village - Village du joueur.
"""

from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

from backend.app.database import Base


class Village(Base):
    """Table des villages (un par joueur)"""
    __tablename__ = "villages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    warehouse_capacity: Mapped[int] = mapped_column(Integer, default=1000, nullable=False)
    moral: Mapped[int] = mapped_column(Integer, default=70, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relations
    user: Mapped["User"] = relationship("User", back_populates="villages")
    characters: Mapped[List["Character"]] = relationship(
        "Character",
        back_populates="village",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    building_instances: Mapped[List["BuildingInstance"]] = relationship(
        "BuildingInstance",
        back_populates="village",
        cascade="all, delete-orphan",
        lazy="select"
    )
    resources: Mapped[List["Resource"]] = relationship(
        "Resource",
        back_populates="village",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    missions: Mapped[List["Mission"]] = relationship(
        "Mission",
        back_populates="village",
        cascade="all, delete-orphan",
        lazy="select"
    )
    researches: Mapped[List["Research"]] = relationship(
        "Research",
        back_populates="village",
        cascade="all, delete-orphan",
        lazy="select"
    )
    relationships: Mapped[List["Relationship"]] = relationship(
        "Relationship",
        back_populates="village",
        cascade="all, delete-orphan",
        lazy="select"
    )
    events: Mapped[List["Event"]] = relationship(
        "Event",
        back_populates="village",
        cascade="all, delete-orphan",
        lazy="select"
    )
    chat_messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage",
        foreign_keys="[ChatMessage.village_id]",
        back_populates="village",
        cascade="all, delete-orphan",
        lazy="select"
    )
    squads: Mapped[List["Squad"]] = relationship(
        "Squad",
        back_populates="village",
        cascade="all, delete-orphan",
        lazy="select"
    )
    achievements: Mapped[List["Achievement"]] = relationship(
        "Achievement",
        back_populates="village",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Village(id={self.id}, name='{self.name}', user_id={self.user_id})>"
