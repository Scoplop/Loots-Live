"""
Modèle Mission - Missions d'exploration.
"""

from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List, Dict, Any

from backend.app.database import Base
from backend.app.utils.constants import MissionType, MissionStatus


class Mission(Base):
    """Table des missions"""
    __tablename__ = "missions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    village_id: Mapped[int] = mapped_column(Integer, ForeignKey("villages.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Informations de base
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    mission_type: Mapped[str] = mapped_column(String(20), nullable=False)  # MissionType enum
    status: Mapped[str] = mapped_column(String(20), default=MissionStatus.PREPARING.value, nullable=False)  # MissionStatus enum
    
    # Difficulté et durée
    difficulty: Mapped[int] = mapped_column(Integer, default=1, nullable=False)  # 1-10
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)  # Durée en minutes
    
    # Récompenses (JSON)
    rewards: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    # Structure:
    # {
    #   "resources": {"water": 50, "food": 30},
    #   "xp": 100,
    #   "equipment_chance": 0.2  # 20% de chance d'équipement
    # }
    
    # Dates
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relations
    village: Mapped["Village"] = relationship("Village", back_populates="missions")
    participants: Mapped[List["MissionParticipant"]] = relationship(
        "MissionParticipant",
        back_populates="mission",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Mission(id={self.id}, name='{self.name}', type='{self.mission_type}', status='{self.status}')>"
