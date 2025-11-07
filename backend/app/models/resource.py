"""
Modèle Resource - Stocks de ressources du village.
"""

from sqlalchemy import Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base
from backend.app.utils.constants import ResourceType


class Resource(Base):
    """Table des stocks de ressources par village"""
    __tablename__ = "resources"
    __table_args__ = (
        UniqueConstraint('village_id', 'resource_type', name='uq_village_resource'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    village_id: Mapped[int] = mapped_column(Integer, ForeignKey("villages.id", ondelete="CASCADE"), nullable=False, index=True)
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # ResourceType enum
    quantity: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relations
    village: Mapped["Village"] = relationship("Village", back_populates="resources")

    def __repr__(self) -> str:
        return f"<Resource(village_id={self.village_id}, type='{self.resource_type}', qty={self.quantity})>"
