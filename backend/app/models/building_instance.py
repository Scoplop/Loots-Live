"""
Modèle BuildingInstance - Instance de bâtiment placée dans un village.
"""

from datetime import datetime
from sqlalchemy import Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

from backend.app.database import Base


class BuildingInstance(Base):
    """Table des instances de bâtiments (bâtiments placés dans les villages)"""
    __tablename__ = "building_instances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    village_id: Mapped[int] = mapped_column(Integer, ForeignKey("villages.id", ondelete="CASCADE"), nullable=False, index=True)
    building_id: Mapped[int] = mapped_column(Integer, ForeignKey("buildings.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Position sur la grille
    grid_x: Mapped[int] = mapped_column(Integer, nullable=False)
    grid_y: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Niveau du bâtiment (pour upgrades futurs)
    level: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # État
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Dates
    built_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_production_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relations
    village: Mapped["Village"] = relationship("Village", back_populates="building_instances")
    building: Mapped["Building"] = relationship("Building", back_populates="instances")
    chat_messages: Mapped[List["ChatMessage"]] = relationship(
        "ChatMessage",
        foreign_keys="[ChatMessage.building_id]",
        back_populates="building",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<BuildingInstance(id={self.id}, building_id={self.building_id}, village_id={self.village_id}, pos=({self.grid_x},{self.grid_y}))>"
