"""
Modèle MissionParticipant - Participation d'un PNJ à une mission.
"""

from sqlalchemy import Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class MissionParticipant(Base):
    """Table de liaison entre missions et personnages participants"""
    __tablename__ = "mission_participants"
    __table_args__ = (
        UniqueConstraint('mission_id', 'character_id', name='uq_mission_character'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[int] = mapped_column(Integer, ForeignKey("missions.id", ondelete="CASCADE"), nullable=False, index=True)
    character_id: Mapped[int] = mapped_column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True)

    # Relations
    mission: Mapped["Mission"] = relationship("Mission", back_populates="participants")
    character: Mapped["Character"] = relationship("Character", back_populates="mission_participations")

    def __repr__(self) -> str:
        return f"<MissionParticipant(mission_id={self.mission_id}, character_id={self.character_id})>"
