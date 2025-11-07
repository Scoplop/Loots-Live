"""
Constantes du jeu Loots&Live.
Toutes les données statiques, énumérations et configurations de gameplay.
"""

from enum import Enum


# ============================================================================
# ÉNUMÉRATIONS
# ============================================================================

class CharacterClass(str, Enum):
    """Classes disponibles pour le PNJ joueur"""
    WARRIOR = "warrior"
    SCOUT = "scout"
    CRAFTSMAN = "craftsman"
    LEADER = "leader"
    SURVIVOR = "survivor"


class Personality(str, Enum):
    """Personnalités des PNJ IA"""
    FRIENDLY = "friendly"
    SHY = "shy"
    AUTHORITARIAN = "authoritarian"
    WISE = "wise"
    JOVIAL = "jovial"
    METHODICAL = "methodical"
    ADVENTURER = "adventurer"
    MATERNAL = "maternal"
    GRUMPY = "grumpy"
    MYSTERIOUS = "mysterious"


class Sex(str, Enum):
    """Sexe des PNJ"""
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"


class EquipmentRarity(str, Enum):
    """Raretés d'équipement"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


class EquipmentSlot(str, Enum):
    """Slots d'équipement"""
    HEAD = "head"
    SHOULDERS = "shoulders"
    TORSO = "torso"
    LEGS = "legs"
    FEET = "feet"
    HANDS = "hands"
    JEWELRY_1 = "jewelry_1"
    JEWELRY_2 = "jewelry_2"
    JEWELRY_3 = "jewelry_3"
    WEAPON_1 = "weapon_1"
    WEAPON_2 = "weapon_2"


class MissionType(str, Enum):
    """Types de missions"""
    HARVEST = "harvest"
    RESCUE = "rescue"
    EXPLORATION = "exploration"


class MissionStatus(str, Enum):
    """Statuts de mission"""
    PREPARING = "preparing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    RECALLED = "recalled"


class ResearchStatus(str, Enum):
    """Statuts de recherche"""
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class BuildingCategory(str, Enum):
    """Catégories de bâtiments"""
    BASE = "base"
    PRODUCTION = "production"
    MILITARY = "military"
    WELLBEING = "wellbeing"
    AUTOMATION = "automation"


class ResearchCategory(str, Enum):
    """Catégories de recherches"""
    AGRICULTURE = "agriculture"
    MILITARY = "military"
    ECONOMY = "economy"
    SCIENCE = "science"


class ResourceType(str, Enum):
    """Types de ressources"""
    # Village (20)
    WATER = "water"
    WOOD = "wood"
    STONE = "stone"
    METAL = "metal"
    FOOD = "food"
    WHEAT = "wheat"
    MEAT = "meat"
    CLOTH = "cloth"
    LEATHER = "leather"
    HERB = "herb"
    BOOK = "book"
    GOLD = "gold"
    SEEDS = "seeds"
    TOOLS = "tools"
    COTTON = "cotton"
    LINEN = "linen"
    PAPER = "paper"
    INK = "ink"
    RARE_ORE = "rare_ore"
    KNOWLEDGE_POINTS = "knowledge_points"
    
    # Mission (10)
    SURVIVAL_KIT = "survival_kit"
    ELECTRONIC_COMPONENT = "electronic_component"
    EXPLOSIVE_POWDER = "explosive_powder"
    GEM = "gem"
    RESIN = "resin"
    ARMOR_PLATE = "armor_plate"
    FUEL = "fuel"
    AMMUNITION = "ammunition"
    MECHANICAL_PARTS = "mechanical_parts"
    ANCIENT_RELIC = "ancient_relic"


class EventType(str, Enum):
    """Types d'événements"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    SPECIAL = "special"


class ChatType(str, Enum):
    """Types de chat"""
    VILLAGE = "village"
    BUILDING = "building"
    PRIVATE = "private"


# ============================================================================
# DONNÉES DE GAMEPLAY
# ============================================================================

# Classes - Stats de base
CLASS_STATS = {
    CharacterClass.WARRIOR: {
        "strength": 3,
        "endurance": 2,
        "speed": 1,
        "dexterity": 0,
        "intelligence": 0,
        "luck": 0,
        "bonus_description": "+10% dégâts mêlée permanents"
    },
    CharacterClass.SCOUT: {
        "strength": 0,
        "dexterity": 3,
        "speed": 2,
        "luck": 1,
        "endurance": 0,
        "intelligence": 0,
        "bonus_description": "+10% dégâts distance permanents"
    },
    CharacterClass.CRAFTSMAN: {
        "strength": 1,
        "dexterity": 2,
        "intelligence": 3,
        "endurance": 0,
        "speed": 0,
        "luck": 0,
        "bonus_description": "-10% coût craft permanents"
    },
    CharacterClass.LEADER: {
        "strength": 0,
        "dexterity": 0,
        "endurance": 2,
        "intelligence": 2,
        "speed": 0,
        "luck": 2,
        "bonus_description": "+5% production globale village"
    },
    CharacterClass.SURVIVOR: {
        "strength": 1,
        "dexterity": 1,
        "endurance": 1,
        "intelligence": 1,
        "speed": 1,
        "luck": 1,
        "bonus_description": "+5% XP gagnée permanents"
    }
}

# Personnalités - Données complètes
PERSONALITY_DATA = {
    Personality.FRIENDLY: {
        "name": "Amical",
        "description": "Chaleureux et accueillant",
        "triggers_positive": ["bonjour", "merci", "aide", "bien"],
        "triggers_negative": ["non", "jamais", "mal", "problème"],
        "relation_impact_positive": 2,
        "relation_impact_negative": -1,
        "mood_modifier": 1,
        "favorite_topics": ["village", "amitié", "entraide"]
    },
    Personality.SHY: {
        "name": "Timide",
        "description": "Hésitant et réservé",
        "triggers_positive": ["gentil", "aide", "comprends", "doucement"],
        "triggers_negative": ["fort", "crier", "urgent", "vite"],
        "relation_impact_positive": 3,
        "relation_impact_negative": -2,
        "mood_modifier": -1,
        "favorite_topics": ["nature", "calme", "livres", "solitude"]
    },
    Personality.AUTHORITARIAN: {
        "name": "Autoritaire",
        "description": "Ferme et directif",
        "triggers_positive": ["respect", "discipline", "ordre", "règles"],
        "triggers_negative": ["désordre", "chaos", "paresse"],
        "relation_impact_positive": 1,
        "relation_impact_negative": -3,
        "mood_modifier": 0,
        "favorite_topics": ["organisation", "responsabilité", "sécurité"]
    },
    Personality.WISE: {
        "name": "Sage",
        "description": "Posé et expérimenté",
        "triggers_positive": ["sagesse", "conseil", "expérience", "calme"],
        "triggers_negative": ["précipitation", "ignorance", "arrogance"],
        "relation_impact_positive": 2,
        "relation_impact_negative": -1,
        "mood_modifier": 1,
        "favorite_topics": ["histoire", "philosophie", "enseignement"]
    },
    Personality.JOVIAL: {
        "name": "Jovial",
        "description": "Joyeux et optimiste",
        "triggers_positive": ["rire", "fête", "joie", "plaisir"],
        "triggers_negative": ["tristesse", "sérieux", "ennui"],
        "relation_impact_positive": 2,
        "relation_impact_negative": -1,
        "mood_modifier": 2,
        "favorite_topics": ["fêtes", "humour", "divertissement"]
    },
    Personality.METHODICAL: {
        "name": "Méthodique",
        "description": "Précis et organisé",
        "triggers_positive": ["plan", "organisation", "efficacité", "précision"],
        "triggers_negative": ["improvisation", "désordre", "chaos"],
        "relation_impact_positive": 1,
        "relation_impact_negative": -2,
        "mood_modifier": 0,
        "favorite_topics": ["organisation", "planification", "optimisation"]
    },
    Personality.ADVENTURER: {
        "name": "Aventurier",
        "description": "Audacieux et explorateur",
        "triggers_positive": ["exploration", "aventure", "découverte", "risque"],
        "triggers_negative": ["routine", "ennui", "sécurité"],
        "relation_impact_positive": 2,
        "relation_impact_negative": -1,
        "mood_modifier": 1,
        "favorite_topics": ["missions", "exploration", "dangers"]
    },
    Personality.MATERNAL: {
        "name": "Maternel",
        "description": "Protecteur et bienveillant",
        "triggers_positive": ["protection", "soin", "famille", "enfants"],
        "triggers_negative": ["danger", "violence", "négligence"],
        "relation_impact_positive": 3,
        "relation_impact_negative": -1,
        "mood_modifier": 1,
        "favorite_topics": ["famille", "santé", "bien-être"]
    },
    Personality.GRUMPY: {
        "name": "Grognon",
        "description": "Râleur et pessimiste",
        "triggers_positive": ["plainte", "problème", "critique"],
        "triggers_negative": ["joie", "optimisme", "fête"],
        "relation_impact_positive": 1,
        "relation_impact_negative": -2,
        "mood_modifier": -2,
        "favorite_topics": ["problèmes", "critiques", "récriminations"]
    },
    Personality.MYSTERIOUS: {
        "name": "Mystérieux",
        "description": "Énigmatique et secret",
        "triggers_positive": ["secret", "mystère", "discrétion", "ombre"],
        "triggers_negative": ["curiosité", "question", "révélation"],
        "relation_impact_positive": 1,
        "relation_impact_negative": -3,
        "mood_modifier": 0,
        "favorite_topics": ["secrets", "mystères", "solitude"]
    }
}

# Compatibilités de personnalités (gain ×1.5 ou perte ×2)
PERSONALITY_COMPATIBLE = [
    (Personality.FRIENDLY, Personality.JOVIAL),
    (Personality.WISE, Personality.METHODICAL),
    (Personality.ADVENTURER, Personality.JOVIAL),
    (Personality.MATERNAL, Personality.FRIENDLY),
    (Personality.METHODICAL, Personality.WISE),
]

PERSONALITY_INCOMPATIBLE = [
    (Personality.AUTHORITARIAN, Personality.GRUMPY),
    (Personality.SHY, Personality.ADVENTURER),
    (Personality.GRUMPY, Personality.JOVIAL),
    (Personality.MYSTERIOUS, Personality.FRIENDLY),
    (Personality.METHODICAL, Personality.ADVENTURER),
]

# Raretés d'équipement - Multiplicateurs
RARITY_MULTIPLIERS = {
    EquipmentRarity.COMMON: 1.0,
    EquipmentRarity.UNCOMMON: 1.15,
    EquipmentRarity.RARE: 1.30,
    EquipmentRarity.EPIC: 1.50,
    EquipmentRarity.LEGENDARY: 1.80,
    EquipmentRarity.MYTHIC: 2.20,
}

# Raretés - Couleurs UI
RARITY_COLORS = {
    EquipmentRarity.COMMON: "#9D9D9D",      # Gris
    EquipmentRarity.UNCOMMON: "#1EFF00",   # Vert
    EquipmentRarity.RARE: "#0070DD",       # Bleu
    EquipmentRarity.EPIC: "#A335EE",       # Violet
    EquipmentRarity.LEGENDARY: "#FF8000",  # Orange
    EquipmentRarity.MYTHIC: "#E6CC80",     # Or/Rouge
}

# Ressources - Poids (pour calcul capacité)
RESOURCE_WEIGHTS = {
    ResourceType.WATER: 1,
    ResourceType.WOOD: 2,
    ResourceType.STONE: 3,
    ResourceType.METAL: 4,
    ResourceType.FOOD: 1,
    ResourceType.WHEAT: 1,
    ResourceType.MEAT: 1,
    ResourceType.CLOTH: 1,
    ResourceType.LEATHER: 2,
    ResourceType.HERB: 1,
    ResourceType.BOOK: 1,
    ResourceType.GOLD: 0,
    ResourceType.SEEDS: 1,
    ResourceType.TOOLS: 3,
    ResourceType.COTTON: 1,
    ResourceType.LINEN: 1,
    ResourceType.PAPER: 0,
    ResourceType.INK: 1,
    ResourceType.RARE_ORE: 2,
    ResourceType.KNOWLEDGE_POINTS: 0,
    ResourceType.SURVIVAL_KIT: 2,
    ResourceType.ELECTRONIC_COMPONENT: 1,
    ResourceType.EXPLOSIVE_POWDER: 3,
    ResourceType.GEM: 1,
    ResourceType.RESIN: 1,
    ResourceType.ARMOR_PLATE: 5,
    ResourceType.FUEL: 2,
    ResourceType.AMMUNITION: 0,
    ResourceType.MECHANICAL_PARTS: 2,
    ResourceType.ANCIENT_RELIC: 1,
}

# Formule XP par niveau
def calculate_xp_for_level(level: int) -> int:
    """Calcule l'XP requise pour atteindre un niveau (formule exponentielle)"""
    return 100 * (level ** 2)

# PV maximum par niveau
def calculate_max_hp(level: int, endurance: int) -> int:
    """Calcule les PV max d'un PNJ"""
    return 100 + (endurance * 10)

# Slots d'équipement disponibles
DEFAULT_EQUIPMENT_SLOTS = [
    EquipmentSlot.HEAD,
    EquipmentSlot.SHOULDERS,
    EquipmentSlot.TORSO,
    EquipmentSlot.LEGS,
    EquipmentSlot.FEET,
    EquipmentSlot.HANDS,
    EquipmentSlot.JEWELRY_1,
    EquipmentSlot.JEWELRY_2,
    EquipmentSlot.JEWELRY_3,
    EquipmentSlot.WEAPON_1,
]

# Points de stats libres à la création
FREE_STAT_POINTS_ON_CREATION = 10

# Limite de caractères pour les champs texte
MAX_USERNAME_LENGTH = 20
MIN_USERNAME_LENGTH = 3
MAX_CHARACTER_NAME_LENGTH = 50
MAX_VILLAGE_NAME_LENGTH = 50
MAX_BIOGRAPHY_LENGTH = 500

# Valeurs par défaut
DEFAULT_WAREHOUSE_CAPACITY = 1000
DEFAULT_MORAL = 70
DEFAULT_HP = 100


# ============================================================================
# ARBRE TECHNOLOGIQUE (RESEARCHES)
# ============================================================================

RESEARCH_TREE = {
    # ========== AGRICULTURE ==========
    "agriculture_1": {
        "name": "Agriculture de base",
        "description": "Techniques agricoles essentielles pour cultiver plus efficacement",
        "category": ResearchCategory.AGRICULTURE,
        "prerequisites": [],
        "costs": {
            "wood": 50,
            "knowledge_points": 10
        },
        "duration_hours": 1,
        "effects": {
            "production_bonus": 10,  # +10% production Food/Wheat
            "unlocks_buildings": ["farm_upgrade"]
        }
    },
    "agriculture_2": {
        "name": "Agriculture avancée",
        "description": "Rotation des cultures et irrigation avancée",
        "category": ResearchCategory.AGRICULTURE,
        "prerequisites": ["agriculture_1"],
        "costs": {
            "wood": 150,
            "seeds": 50,
            "knowledge_points": 25
        },
        "duration_hours": 3,
        "effects": {
            "production_bonus": 15,
            "unlocks_buildings": ["greenhouse"]
        }
    },
    "livestock": {
        "name": "Élevage",
        "description": "Domestication et élevage d'animaux",
        "category": ResearchCategory.AGRICULTURE,
        "prerequisites": ["agriculture_1"],
        "costs": {
            "wood": 100,
            "food": 50,
            "knowledge_points": 20
        },
        "duration_hours": 2,
        "effects": {
            "production_bonus": 10,
            "unlocks_buildings": ["stable"]
        }
    },
    "herbalism": {
        "name": "Herboristerie",
        "description": "Connaissance des plantes médicinales",
        "category": ResearchCategory.AGRICULTURE,
        "prerequisites": ["agriculture_1"],
        "costs": {
            "herb": 30,
            "book": 5,
            "knowledge_points": 15
        },
        "duration_hours": 2,
        "effects": {
            "production_bonus": 10,
            "special_ability": "heal_boost"  # +20% efficacité soins
        }
    },
    "irrigation": {
        "name": "Irrigation avancée",
        "description": "Systèmes d'irrigation sophistiqués",
        "category": ResearchCategory.AGRICULTURE,
        "prerequisites": ["agriculture_2"],
        "costs": {
            "stone": 200,
            "metal": 100,
            "knowledge_points": 40
        },
        "duration_hours": 5,
        "effects": {
            "production_bonus": 25,
            "construction_speed_bonus": 10
        }
    },
    
    # ========== MILITARY ==========
    "basic_weapons": {
        "name": "Armement de base",
        "description": "Fabrication d'armes simples",
        "category": ResearchCategory.MILITARY,
        "prerequisites": [],
        "costs": {
            "wood": 50,
            "metal": 30,
            "knowledge_points": 10
        },
        "duration_hours": 1,
        "effects": {
            "mission_success_bonus": 5,
            "unlocks_equipment": ["iron_sword", "wooden_bow"]
        }
    },
    "basic_armor": {
        "name": "Armures de base",
        "description": "Fabrication d'armures simples",
        "category": ResearchCategory.MILITARY,
        "prerequisites": [],
        "costs": {
            "leather": 40,
            "metal": 20,
            "knowledge_points": 10
        },
        "duration_hours": 1,
        "effects": {
            "mission_success_bonus": 5,
            "unlocks_equipment": ["leather_armor", "iron_helmet"]
        }
    },
    "advanced_weapons": {
        "name": "Armement avancé",
        "description": "Armes de qualité supérieure",
        "category": ResearchCategory.MILITARY,
        "prerequisites": ["basic_weapons"],
        "costs": {
            "metal": 150,
            "rare_ore": 50,
            "knowledge_points": 30
        },
        "duration_hours": 4,
        "effects": {
            "mission_success_bonus": 10,
            "unlocks_equipment": ["steel_sword", "crossbow", "pike"]
        }
    },
    "advanced_armor": {
        "name": "Armures avancées",
        "description": "Protection renforcée",
        "category": ResearchCategory.MILITARY,
        "prerequisites": ["basic_armor"],
        "costs": {
            "metal": 200,
            "cloth": 100,
            "knowledge_points": 30
        },
        "duration_hours": 4,
        "effects": {
            "mission_success_bonus": 10,
            "unlocks_equipment": ["steel_armor", "chainmail"]
        }
    },
    "tactics": {
        "name": "Tactiques militaires",
        "description": "Formation et stratégie de combat",
        "category": ResearchCategory.MILITARY,
        "prerequisites": ["basic_weapons", "basic_armor"],
        "costs": {
            "book": 10,
            "knowledge_points": 25
        },
        "duration_hours": 3,
        "effects": {
            "mission_success_bonus": 15,
            "special_ability": "tactical_advantage"
        }
    },
    "fortification": {
        "name": "Fortification",
        "description": "Murs et défenses avancées",
        "category": ResearchCategory.MILITARY,
        "prerequisites": ["tactics"],
        "costs": {
            "stone": 300,
            "wood": 200,
            "knowledge_points": 35
        },
        "duration_hours": 6,
        "effects": {
            "unlocks_buildings": ["guard_tower", "wall"]
        }
    },
    
    # ========== ECONOMY ==========
    "basic_trade": {
        "name": "Commerce de base",
        "description": "Principes fondamentaux du commerce",
        "category": ResearchCategory.ECONOMY,
        "prerequisites": [],
        "costs": {
            "gold": 50,
            "knowledge_points": 10
        },
        "duration_hours": 1,
        "effects": {
            "production_bonus": 5,
            "unlocks_buildings": ["market"]
        }
    },
    "advanced_trade": {
        "name": "Commerce avancé",
        "description": "Routes commerciales et négociation",
        "category": ResearchCategory.ECONOMY,
        "prerequisites": ["basic_trade"],
        "costs": {
            "gold": 200,
            "paper": 50,
            "knowledge_points": 30
        },
        "duration_hours": 4,
        "effects": {
            "production_bonus": 10,
            "special_ability": "better_prices"  # -15% coûts, +15% ventes
        }
    },
    "craftsmanship": {
        "name": "Artisanat",
        "description": "Techniques de fabrication améliorées",
        "category": ResearchCategory.ECONOMY,
        "prerequisites": [],
        "costs": {
            "wood": 100,
            "metal": 50,
            "knowledge_points": 15
        },
        "duration_hours": 2,
        "effects": {
            "production_bonus": 10,
            "unlocks_buildings": ["workshop"]
        }
    },
    "metallurgy": {
        "name": "Métallurgie",
        "description": "Travail avancé des métaux",
        "category": ResearchCategory.ECONOMY,
        "prerequisites": ["craftsmanship"],
        "costs": {
            "metal": 200,
            "rare_ore": 100,
            "knowledge_points": 35
        },
        "duration_hours": 5,
        "effects": {
            "production_bonus": 15,
            "unlocks_buildings": ["foundry"],
            "unlocks_equipment": ["mithril_gear"]
        }
    },
    "textile_industry": {
        "name": "Industrie textile",
        "description": "Production de tissus de qualité",
        "category": ResearchCategory.ECONOMY,
        "prerequisites": ["craftsmanship"],
        "costs": {
            "cotton": 150,
            "linen": 100,
            "knowledge_points": 25
        },
        "duration_hours": 3,
        "effects": {
            "production_bonus": 15,
            "unlocks_buildings": ["textile_mill"]
        }
    },
    "mining": {
        "name": "Exploitation minière",
        "description": "Techniques d'extraction avancées",
        "category": ResearchCategory.ECONOMY,
        "prerequisites": ["craftsmanship"],
        "costs": {
            "tools": 100,
            "stone": 150,
            "knowledge_points": 30
        },
        "duration_hours": 4,
        "effects": {
            "production_bonus": 20,
            "unlocks_buildings": ["mine"]
        }
    },
    
    # ========== SCIENCE ==========
    "basic_research": {
        "name": "Recherche de base",
        "description": "Méthode scientifique et observation",
        "category": ResearchCategory.SCIENCE,
        "prerequisites": [],
        "costs": {
            "book": 5,
            "knowledge_points": 10
        },
        "duration_hours": 1,
        "effects": {
            "research_speed_bonus": 10,
            "unlocks_buildings": ["library"]
        }
    },
    "advanced_research": {
        "name": "Recherche avancée",
        "description": "Laboratoires et expérimentation",
        "category": ResearchCategory.SCIENCE,
        "prerequisites": ["basic_research"],
        "costs": {
            "book": 20,
            "paper": 100,
            "ink": 50,
            "knowledge_points": 40
        },
        "duration_hours": 5,
        "effects": {
            "research_speed_bonus": 20,
            "unlocks_buildings": ["laboratory"]
        }
    },
    "medicine": {
        "name": "Médecine",
        "description": "Soins et traitement des blessures",
        "category": ResearchCategory.SCIENCE,
        "prerequisites": ["basic_research", "herbalism"],
        "costs": {
            "herb": 100,
            "book": 10,
            "knowledge_points": 30
        },
        "duration_hours": 4,
        "effects": {
            "special_ability": "faster_healing",  # +50% régénération HP
            "unlocks_buildings": ["infirmary"]
        }
    },
    "engineering": {
        "name": "Ingénierie",
        "description": "Machines et constructions complexes",
        "category": ResearchCategory.SCIENCE,
        "prerequisites": ["basic_research", "craftsmanship"],
        "costs": {
            "metal": 200,
            "tools": 150,
            "knowledge_points": 40
        },
        "duration_hours": 6,
        "effects": {
            "construction_speed_bonus": 25,
            "production_bonus": 15
        }
    },
    "alchemy": {
        "name": "Alchimie",
        "description": "Transformation et potions",
        "category": ResearchCategory.SCIENCE,
        "prerequisites": ["medicine", "advanced_research"],
        "costs": {
            "herb": 200,
            "rare_ore": 100,
            "gem": 50,
            "knowledge_points": 50
        },
        "duration_hours": 8,
        "effects": {
            "special_ability": "alchemy_transmutation",
            "unlocks_buildings": ["alchemy_lab"]
        }
    },
    "ancient_knowledge": {
        "name": "Savoirs anciens",
        "description": "Redécouverte des technologies perdues",
        "category": ResearchCategory.SCIENCE,
        "prerequisites": ["advanced_research", "alchemy"],
        "costs": {
            "ancient_relic": 10,
            "book": 50,
            "knowledge_points": 100
        },
        "duration_hours": 12,
        "effects": {
            "research_speed_bonus": 30,
            "production_bonus": 20,
            "mission_success_bonus": 15,
            "special_ability": "ancient_power"
        }
    }
}
