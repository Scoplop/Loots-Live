"""
Package des modèles SQLAlchemy.
Tous les modèles sont importés ici pour faciliter l'accès et résoudre les dépendances circulaires.
"""

from backend.app.models.user import User
from backend.app.models.village import Village
from backend.app.models.character import Character
from backend.app.models.building import Building
from backend.app.models.building_instance import BuildingInstance
from backend.app.models.resource import Resource
from backend.app.models.equipment import Equipment
from backend.app.models.mission import Mission
from backend.app.models.mission_participant import MissionParticipant
from backend.app.models.research import Research
from backend.app.models.relationship import Relationship
from backend.app.models.relationship_history import RelationshipHistory
from backend.app.models.event import Event
from backend.app.models.village_ai import VillageAI
from backend.app.models.chat_message import ChatMessage
from backend.app.models.squad import Squad
from backend.app.models.squad_member import SquadMember
from backend.app.models.achievement import Achievement

__all__ = [
    "User",
    "Village",
    "Character",
    "Building",
    "BuildingInstance",
    "Resource",
    "Equipment",
    "Mission",
    "MissionParticipant",
    "Research",
    "Relationship",
    "RelationshipHistory",
    "Event",
    "VillageAI",
    "ChatMessage",
    "Squad",
    "SquadMember",
    "Achievement",
]

