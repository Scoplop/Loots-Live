"""
Service pour la gestion des personnages (PNJ joueur et IA).
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
import random

from backend.app.models.character import Character
from backend.app.models.user import User
from backend.app.models.village import Village
from backend.app.schemas.character import (
    CharacterCreate,
    CharacterCreateAI,
    CharacterResponse,
    CharacterUpdate,
    CharacterAllocateStats,
    CharacterStats
)
from backend.app.utils.constants import (
    CharacterClass,
    Personality,
    Sex,
    CLASS_STATS,
    PERSONALITY_DATA,
    FREE_STAT_POINTS_ON_CREATION,
    calculate_max_hp,
    calculate_xp_for_level
)


class CharacterService:
    """Service pour gérer les personnages"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_player_character(
        self,
        user_id: int,
        character_data: CharacterCreate
    ) -> Character:
        """
        Crée le PNJ joueur (obligatoire après inscription).
        Un joueur ne peut avoir qu'UN SEUL personnage joueur.
        """
        # Vérifier que l'utilisateur existe
        user_result = await self.db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )

        # Vérifier que l'utilisateur n'a pas déjà un PNJ joueur
        existing_pc_result = await self.db.execute(
            select(Character).where(
                Character.user_id == user_id,
                Character.is_player_character == True
            )
        )
        existing_pc = existing_pc_result.scalar_one_or_none()
        if existing_pc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vous avez déjà créé votre personnage joueur"
            )

        # Récupérer le village de l'utilisateur
        village_result = await self.db.execute(
            select(Village).where(Village.user_id == user_id)
        )
        village = village_result.scalar_one_or_none()
        if not village:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Village non trouvé. Créez d'abord un village."
            )

        # Valider l'allocation de stats (max 10 points libres + bonus de classe)
        total_allocated = (
            character_data.strength +
            character_data.dexterity +
            character_data.endurance +
            character_data.intelligence +
            character_data.speed +
            character_data.luck
        )

        # Récupérer les bonus de classe
        class_bonuses = CLASS_STATS.get(character_data.character_class)
        if not class_bonuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Classe de personnage invalide"
            )

        class_total = sum([
            class_bonuses["strength"],
            class_bonuses["dexterity"],
            class_bonuses["endurance"],
            class_bonuses["intelligence"],
            class_bonuses["speed"],
            class_bonuses["luck"]
        ])

        max_allowed = FREE_STAT_POINTS_ON_CREATION + class_total
        if total_allocated > max_allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Allocation de stats invalide. Maximum autorisé: {max_allowed} points (10 libres + {class_total} bonus de classe)"
            )

        # Calculer les HP max
        max_hp = calculate_max_hp(1, character_data.endurance)

        # Créer le personnage
        new_character = Character(
            user_id=user_id,
            village_id=village.id,
            name=character_data.name,
            biography=character_data.biography,
            is_player_character=True,
            character_class=character_data.character_class.value,
            sex=character_data.sex.value,
            personality=None,  # PNJ joueur n'a pas de personnalité
            level=1,
            xp=0,
            free_stat_points=max_allowed - total_allocated,
            strength=character_data.strength,
            dexterity=character_data.dexterity,
            endurance=character_data.endurance,
            intelligence=character_data.intelligence,
            speed=character_data.speed,
            luck=character_data.luck,
            current_hp=max_hp,
            max_hp=max_hp,
            is_on_mission=False,
            appearance=character_data.appearance or {},
            equipment={}
        )

        self.db.add(new_character)
        await self.db.commit()
        await self.db.refresh(new_character)

        return new_character

    async def create_ai_character(
        self,
        user_id: int,
        character_data: CharacterCreateAI
    ) -> Character:
        """
        Crée un PNJ IA avec génération aléatoire des stats.
        Stats aléatoires entre 0-5 par stat, + bonus de classe.
        """
        # Vérifier que l'utilisateur existe
        user_result = await self.db.execute(select(User).where(User.id == user_id))
        user = user_result.scalar_one_or_none()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )

        # Récupérer le village
        village_result = await self.db.execute(
            select(Village).where(Village.user_id == user_id)
        )
        village = village_result.scalar_one_or_none()
        if not village:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Village non trouvé"
            )

        # Valider la personnalité
        if character_data.personality not in PERSONALITY_DATA:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Personnalité invalide"
            )

        # Récupérer les bonus de classe
        class_bonuses = CLASS_STATS.get(character_data.character_class)
        if not class_bonuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Classe invalide"
            )

        # Générer des stats aléatoires (0-5 par stat)
        random_stats = {
            "strength": random.randint(0, 5),
            "dexterity": random.randint(0, 5),
            "endurance": random.randint(0, 5),
            "intelligence": random.randint(0, 5),
            "speed": random.randint(0, 5),
            "luck": random.randint(0, 5)
        }

        # Ajouter les bonus de classe
        total_strength = random_stats["strength"] + class_bonuses["strength"]
        total_dexterity = random_stats["dexterity"] + class_bonuses["dexterity"]
        total_endurance = random_stats["endurance"] + class_bonuses["endurance"]
        total_intelligence = random_stats["intelligence"] + class_bonuses["intelligence"]
        total_speed = random_stats["speed"] + class_bonuses["speed"]
        total_luck = random_stats["luck"] + class_bonuses["luck"]

        # Calculer HP max
        max_hp = calculate_max_hp(1, total_endurance)

        # Générer apparence aléatoire si non fournie
        appearance = character_data.appearance or self._generate_random_appearance(character_data.sex)

        # Créer le PNJ IA
        new_character = Character(
            user_id=user_id,
            village_id=village.id,
            name=character_data.name,
            biography=character_data.biography,
            is_player_character=False,
            character_class=character_data.character_class.value,
            personality=character_data.personality.value,
            sex=character_data.sex.value,
            level=1,
            xp=0,
            free_stat_points=0,  # PNJ IA n'ont pas de points libres
            strength=total_strength,
            dexterity=total_dexterity,
            endurance=total_endurance,
            intelligence=total_intelligence,
            speed=total_speed,
            luck=total_luck,
            current_hp=max_hp,
            max_hp=max_hp,
            is_on_mission=False,
            appearance=appearance,
            equipment={}
        )

        self.db.add(new_character)
        await self.db.commit()
        await self.db.refresh(new_character)

        return new_character

    async def get_character_by_id(
        self,
        character_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Character]:
        """Récupère un personnage par ID (avec vérification propriétaire optionnelle)"""
        query = select(Character).where(Character.id == character_id)
        
        if user_id:
            query = query.where(Character.user_id == user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_player_character(self, user_id: int) -> Optional[Character]:
        """Récupère le PNJ joueur de l'utilisateur"""
        result = await self.db.execute(
            select(Character).where(
                Character.user_id == user_id,
                Character.is_player_character == True
            )
        )
        return result.scalar_one_or_none()

    async def get_all_village_characters(self, user_id: int) -> List[Character]:
        """Récupère tous les personnages du village (joueur + IA)"""
        # Récupérer le village
        village_result = await self.db.execute(
            select(Village).where(Village.user_id == user_id)
        )
        village = village_result.scalar_one_or_none()
        if not village:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Village non trouvé"
            )

        result = await self.db.execute(
            select(Character)
            .where(Character.village_id == village.id)
            .order_by(Character.is_player_character.desc(), Character.name)
        )
        return list(result.scalars().all())

    async def get_ai_characters(self, user_id: int) -> List[Character]:
        """Récupère uniquement les PNJ IA du village"""
        village_result = await self.db.execute(
            select(Village).where(Village.user_id == user_id)
        )
        village = village_result.scalar_one_or_none()
        if not village:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Village non trouvé"
            )

        result = await self.db.execute(
            select(Character)
            .where(
                Character.village_id == village.id,
                Character.is_player_character == False
            )
            .order_by(Character.name)
        )
        return list(result.scalars().all())

    async def update_character(
        self,
        character_id: int,
        user_id: int,
        character_data: CharacterUpdate
    ) -> Character:
        """Met à jour les informations d'un personnage (nom, bio, apparence)"""
        character = await self.get_character_by_id(character_id, user_id)
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personnage non trouvé"
            )

        # Mettre à jour uniquement les champs fournis
        if character_data.name is not None:
            character.name = character_data.name
        if character_data.biography is not None:
            character.biography = character_data.biography
        if character_data.appearance is not None:
            character.appearance = character_data.appearance

        await self.db.commit()
        await self.db.refresh(character)
        return character

    async def allocate_stats(
        self,
        character_id: int,
        user_id: int,
        stats_data: CharacterAllocateStats
    ) -> Character:
        """
        Alloue les points de stats libres (PNJ joueur uniquement).
        Vérifie qu'il y a assez de points libres disponibles.
        """
        character = await self.get_character_by_id(character_id, user_id)
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personnage non trouvé"
            )

        if not character.is_player_character:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Seul le personnage joueur peut allouer des points de stats"
            )

        # Calculer les points alloués
        points_allocated = (
            stats_data.strength +
            stats_data.dexterity +
            stats_data.endurance +
            stats_data.intelligence +
            stats_data.speed +
            stats_data.luck
        )

        if points_allocated > character.free_stat_points:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Pas assez de points libres. Disponibles: {character.free_stat_points}"
            )

        # Allouer les stats
        character.strength += stats_data.strength
        character.dexterity += stats_data.dexterity
        character.endurance += stats_data.endurance
        character.intelligence += stats_data.intelligence
        character.speed += stats_data.speed
        character.luck += stats_data.luck
        character.free_stat_points -= points_allocated

        # Recalculer HP max si endurance augmente
        new_max_hp = calculate_max_hp(character.level, character.endurance)
        hp_increase = new_max_hp - character.max_hp
        character.max_hp = new_max_hp
        character.current_hp += hp_increase  # Augmenter aussi les HP actuels

        await self.db.commit()
        await self.db.refresh(character)
        return character

    async def calculate_power_score(self, character_id: int) -> int:
        """
        Calcule le score de puissance d'un personnage.
        Score = Somme stats + Bonus équipement (à implémenter avec Equipment service)
        """
        character = await self.get_character_by_id(character_id)
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personnage non trouvé"
            )

        # Score de base = somme des stats
        base_score = (
            character.strength +
            character.dexterity +
            character.endurance +
            character.intelligence +
            character.speed +
            character.luck
        )

        # TODO: Ajouter bonus équipement quand Equipment service sera créé
        equipment_bonus = 0

        return base_score + equipment_bonus

    async def get_character_stats(self, character_id: int) -> CharacterStats:
        """
        Récupère les statistiques complètes d'un personnage.
        Inclut stats de base, stats avec équipement, HP, niveau, etc.
        """
        character = await self.get_character_by_id(character_id)
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personnage non trouvé"
            )

        # Stats de base
        base_stats = {
            "strength": character.strength,
            "dexterity": character.dexterity,
            "endurance": character.endurance,
            "intelligence": character.intelligence,
            "speed": character.speed,
            "luck": character.luck
        }

        # TODO: Calculer bonus équipement quand Equipment service sera créé
        equipment_bonuses = {
            "strength": 0,
            "dexterity": 0,
            "endurance": 0,
            "intelligence": 0,
            "speed": 0,
            "luck": 0,
            "armor": 0,
            "damage": 0
        }

        # Stats totales
        total_stats = {
            "total_strength": base_stats["strength"] + equipment_bonuses["strength"],
            "total_dexterity": base_stats["dexterity"] + equipment_bonuses["dexterity"],
            "total_endurance": base_stats["endurance"] + equipment_bonuses["endurance"],
            "total_intelligence": base_stats["intelligence"] + equipment_bonuses["intelligence"],
            "total_speed": base_stats["speed"] + equipment_bonuses["speed"],
            "total_luck": base_stats["luck"] + equipment_bonuses["luck"],
            "total_armor": equipment_bonuses["armor"],
            "total_damage": equipment_bonuses["damage"]
        }

        # Récupérer le bonus de classe
        class_bonus = CLASS_STATS.get(CharacterClass(character.character_class))
        class_description = class_bonus["bonus_description"] if class_bonus else "Aucun"

        # XP pour niveau suivant
        xp_to_next = calculate_xp_for_level(character.level + 1)

        return CharacterStats(
            **base_stats,
            **total_stats,
            current_hp=character.current_hp,
            max_hp=character.max_hp,
            level=character.level,
            xp=character.xp,
            xp_to_next_level=xp_to_next - character.xp,
            class_bonus=class_description
        )

    async def delete_character(self, character_id: int, user_id: int) -> bool:
        """
        Supprime un PNJ IA (impossible de supprimer le PNJ joueur).
        """
        character = await self.get_character_by_id(character_id, user_id)
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personnage non trouvé"
            )

        if character.is_player_character:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de supprimer le personnage joueur"
            )

        if character.is_on_mission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de supprimer un personnage en mission"
            )

        await self.db.delete(character)
        await self.db.commit()
        return True

    async def gain_xp(self, character_id: int, xp_amount: int) -> Character:
        """
        Ajoute de l'XP à un personnage et gère les montées de niveau.
        À chaque niveau: +1 point libre, recalcul HP max.
        """
        character = await self.get_character_by_id(character_id)
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personnage non trouvé"
            )

        character.xp += xp_amount
        
        # Vérifier montée de niveau
        while character.xp >= calculate_xp_for_level(character.level + 1):
            character.level += 1
            if character.is_player_character:
                character.free_stat_points += 1
            
            # Recalculer HP max et restaurer HP
            new_max_hp = calculate_max_hp(character.level, character.endurance)
            hp_increase = new_max_hp - character.max_hp
            character.max_hp = new_max_hp
            character.current_hp += hp_increase

        await self.db.commit()
        await self.db.refresh(character)
        return character

    async def heal_character(self, character_id: int, heal_amount: int) -> Character:
        """Soigne un personnage (ne peut pas dépasser max_hp)"""
        character = await self.get_character_by_id(character_id)
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personnage non trouvé"
            )

        character.current_hp = min(character.current_hp + heal_amount, character.max_hp)
        
        await self.db.commit()
        await self.db.refresh(character)
        return character

    async def damage_character(self, character_id: int, damage_amount: int) -> Character:
        """Inflige des dégâts à un personnage (peut tomber à 0 HP)"""
        character = await self.get_character_by_id(character_id)
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personnage non trouvé"
            )

        character.current_hp = max(0, character.current_hp - damage_amount)
        
        await self.db.commit()
        await self.db.refresh(character)
        return character

    def _generate_random_appearance(self, sex: Sex) -> Dict[str, Any]:
        """Génère une apparence aléatoire pour un PNJ IA"""
        hair_colors = ["#000000", "#3B2414", "#8B4513", "#D2691E", "#FFD700", "#FF6347", "#FFFFFF"]
        skin_tones = ["#FFDBAC", "#F1C27D", "#E0AC69", "#C68642", "#8D5524", "#654321"]
        eye_colors = ["#8B4513", "#228B22", "#4169E1", "#A9A9A9", "#32CD32", "#000000"]
        
        hair_styles = ["short", "long", "bald", "ponytail", "braids", "curly"] if sex == Sex.FEMALE else ["short", "long", "bald", "crew_cut", "spiky"]
        facial_hair = ["none"] if sex == Sex.FEMALE else ["none", "beard", "goatee", "mustache", "stubble"]
        
        return {
            "hair_color": random.choice(hair_colors),
            "hair_style": random.choice(hair_styles),
            "skin_tone": random.choice(skin_tones),
            "eye_color": random.choice(eye_colors),
            "facial_hair": random.choice(facial_hair),
            "accessories": [],
            "scars": [],
            "tattoos": []
        }
