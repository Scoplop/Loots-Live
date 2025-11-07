"""
Modèle Squad - Équipes de PNJ.
"""

from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from backend.app.database import Base


class Squad(Base):
    """Table des équipes (groupes de PNJ)"""
    __tablename__ = "squads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    village_id: Mapped[int] = mapped_column(Integer, ForeignKey("villages.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Informations de base
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Date de création
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relations
    village: Mapped["Village"] = relationship("Village", back_populates="squads")
    members: Mapped[List["SquadMember"]] = relationship(
        "SquadMember",
        back_populates="squad",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Squad(id={self.id}, name='{self.name}', village_id={self.village_id})>"
