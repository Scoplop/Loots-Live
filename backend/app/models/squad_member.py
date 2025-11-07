"""
Modèle SquadMember - Membre d'une équipe.
"""

from sqlalchemy import Integer, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


class SquadMember(Base):
    """Table de liaison entre squads et personnages"""
    __tablename__ = "squad_members"
    __table_args__ = (
        UniqueConstraint('squad_id', 'character_id', name='uq_squad_character'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    squad_id: Mapped[int] = mapped_column(Integer, ForeignKey("squads.id", ondelete="CASCADE"), nullable=False, index=True)
    character_id: Mapped[int] = mapped_column(Integer, ForeignKey("characters.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Rôle dans l'équipe
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    # "leader", "member", "specialist"

    # Relations
    squad: Mapped["Squad"] = relationship("Squad", back_populates="members")
    character: Mapped["Character"] = relationship("Character", back_populates="squad_memberships")

    def __repr__(self) -> str:
        return f"<SquadMember(squad_id={self.squad_id}, character_id={self.character_id}, role='{self.role}')>"
