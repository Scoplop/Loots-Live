"""
Modèle Relationship - Relations entre PNJ.
"""

from datetime import datetime
from sqlalchemy import Integer, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from backend.app.database import Base


class Relationship(Base):
    """Table des relations entre PNJ (-100 à +100)"""
    __tablename__ = "relationships"
    __table_args__ = (
        UniqueConstraint('village_id', 'character_id', 'target_character_id', name='uq_relationship'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    village_id: Mapped[int] = mapped_column(Integer, ForeignKey("villages.id", ondelete="CASCADE"), nullable=False, index=True)
    character_id: Mapped[int] = mapped_column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True)
    target_character_id: Mapped[int] = mapped_column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Score de relation (-100 haine → +100 amitié)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Date de dernière modification
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relations
    village: Mapped["Village"] = relationship("Village", back_populates="relationships")
    character: Mapped["Character"] = relationship(
        "Character",
        foreign_keys=[character_id],
        back_populates="relationships_as_source"
    )
    target_character: Mapped["Character"] = relationship(
        "Character",
        foreign_keys=[target_character_id],
        back_populates="relationships_as_target"
    )
    history: Mapped[List["RelationshipHistory"]] = relationship(
        "RelationshipHistory",
        back_populates="relationship",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self) -> str:
        return f"<Relationship(char={self.character_id} → target={self.target_character_id}, score={self.score})>"
