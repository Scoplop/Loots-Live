"""
Modèle VillageAI - Villages IA pour diplomatie.
"""

from datetime import datetime
from sqlalchemy import Integer, String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.database import Base


class VillageAI(Base):
    """Table des villages IA (pour diplomatie et commerce)"""
    __tablename__ = "villages_ai"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Informations de base
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Politique et relations
    disposition: Mapped[str] = mapped_column(String(20), nullable=False)
    # "friendly", "neutral", "hostile", "allied"
    
    military_strength: Mapped[int] = mapped_column(Integer, default=100, nullable=False)  # 1-1000
    wealth: Mapped[int] = mapped_column(Integer, default=100, nullable=False)  # 1-1000
    
    # Position géographique (pour futures fonctionnalités)
    world_x: Mapped[int] = mapped_column(Integer, nullable=False)
    world_y: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Date de création
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<VillageAI(id={self.id}, name='{self.name}', disposition='{self.disposition}')>"
