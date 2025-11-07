"""
Package des schémas Pydantic.
Tous les schémas sont importés ici pour faciliter l'accès.
"""

# User & Auth
from backend.app.schemas.user import (
    UserBase,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
    Token,
    TokenData,
)

# Village
from backend.app.schemas.village import (
    VillageBase,
    VillageCreate,
    VillageUpdate,
    VillageResponse,
    VillageStats,
)

# Character
from backend.app.schemas.character import (
    CharacterBase,
    CharacterCreate,
    CharacterCreateAI,
    CharacterResponse,
    CharacterUpdate,
    CharacterAllocateStats,
    CharacterEquip,
    CharacterStats,
)

# Resource
from backend.app.schemas.resource import (
    ResourceBase,
    ResourceCreate,
    ResourceUpdate,
    ResourceResponse,
    ResourceAdd,
    ResourceRemove,
    ResourceCost,
    ResourceInventory,
)

# Building
from backend.app.schemas.building import (
    BuildingBase,
    BuildingResponse,
    BuildingInstanceBase,
    BuildingInstanceCreate,
    BuildingInstanceResponse,
    BuildingInstanceWithDetails,
    BuildingBuild,
    BuildingDestroy,
    BuildingProduction,
)

# Equipment
from backend.app.schemas.equipment import (
    EquipmentBase,
    EquipmentCreate,
    EquipmentResponse,
    EquipmentGenerate,
)

# Mission
from backend.app.schemas.mission import (
    MissionBase,
    MissionCreate,
    MissionResponse,
    MissionWithParticipants,
    MissionStart,
    MissionRecall,
    MissionComplete,
)

# Research
from backend.app.schemas.research import (
    ResearchBase,
    ResearchCreate,
    ResearchResponse,
    ResearchStart,
    ResearchProgress,
)

# Relationship
from backend.app.schemas.relationship import (
    RelationshipBase,
    RelationshipCreate,
    RelationshipResponse,
    RelationshipUpdate,
    RelationshipHistoryResponse,
    RelationshipGraph,
)

# Event
from backend.app.schemas.event import (
    EventBase,
    EventCreate,
    EventResponse,
    EventTrigger,
)

# Chat
from backend.app.schemas.chat import (
    ChatMessageBase,
    ChatMessageCreate,
    ChatMessageResponse,
    ChatContext,
    ChatResponse,
)

# Squad
from backend.app.schemas.squad import (
    SquadBase,
    SquadCreate,
    SquadResponse,
    SquadMemberResponse,
    SquadWithMembers,
    SquadAddMember,
    SquadRemoveMember,
)

# Achievement
from backend.app.schemas.achievement import (
    AchievementBase,
    AchievementCreate,
    AchievementResponse,
    AchievementUnlock,
)

__all__ = [
    # User & Auth
    "UserBase",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserUpdate",
    "Token",
    "TokenData",
    # Village
    "VillageBase",
    "VillageCreate",
    "VillageUpdate",
    "VillageResponse",
    "VillageStats",
    # Character
    "CharacterBase",
    "CharacterCreate",
    "CharacterCreateAI",
    "CharacterResponse",
    "CharacterUpdate",
    "CharacterAllocateStats",
    "CharacterEquip",
    "CharacterStats",
    # Resource
    "ResourceBase",
    "ResourceCreate",
    "ResourceUpdate",
    "ResourceResponse",
    "ResourceAdd",
    "ResourceRemove",
    "ResourceCost",
    "ResourceInventory",
    # Building
    "BuildingBase",
    "BuildingResponse",
    "BuildingInstanceBase",
    "BuildingInstanceCreate",
    "BuildingInstanceResponse",
    "BuildingInstanceWithDetails",
    "BuildingBuild",
    "BuildingDestroy",
    "BuildingProduction",
    # Equipment
    "EquipmentBase",
    "EquipmentCreate",
    "EquipmentResponse",
    "EquipmentGenerate",
    # Mission
    "MissionBase",
    "MissionCreate",
    "MissionResponse",
    "MissionWithParticipants",
    "MissionStart",
    "MissionRecall",
    "MissionComplete",
    # Research
    "ResearchBase",
    "ResearchCreate",
    "ResearchResponse",
    "ResearchStart",
    "ResearchProgress",
    # Relationship
    "RelationshipBase",
    "RelationshipCreate",
    "RelationshipResponse",
    "RelationshipUpdate",
    "RelationshipHistoryResponse",
    "RelationshipGraph",
    # Event
    "EventBase",
    "EventCreate",
    "EventResponse",
    "EventTrigger",
    # Chat
    "ChatMessageBase",
    "ChatMessageCreate",
    "ChatMessageResponse",
    "ChatContext",
    "ChatResponse",
    # Squad
    "SquadBase",
    "SquadCreate",
    "SquadResponse",
    "SquadMemberResponse",
    "SquadWithMembers",
    "SquadAddMember",
    "SquadRemoveMember",
    # Achievement
    "AchievementBase",
    "AchievementCreate",
    "AchievementResponse",
    "AchievementUnlock",
]

