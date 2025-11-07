"""
Modèle Achievement - Succès débloqués.
"""

from datetime import datetime
from sqlalchemy import Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class Achievement(Base):
    """Table des succès débloqués"""
    __tablename__ = "achievements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    village_id: Mapped[int] = mapped_column(Integer, ForeignKey("villages.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Informations du succès
    key: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    # Identifiant unique (ex: "first_mission", "level_10_character")
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Récompense XP/ressources
    reward_xp: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Date de déverrouillage
    unlocked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relations
    village: Mapped["Village"] = relationship("Village", back_populates="achievements")

    def __repr__(self) -> str:
        return f"<Achievement(id={self.id}, key='{self.key}', village_id={self.village_id})>"
