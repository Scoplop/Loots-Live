"""
Service pour la gestion des équipements.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
import random

from backend.app.models.equipment import Equipment
from backend.app.models.character import Character
from backend.app.models.village import Village
from backend.app.schemas.equipment import (
    EquipmentCreate,
    EquipmentResponse,
    EquipmentGenerate
)
from backend.app.utils.constants import (
    EquipmentRarity,
    EquipmentSlot,
    RARITY_MULTIPLIERS
)


class EquipmentService:
    """Service pour gérer les équipements"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_equipment(
        self,
        character_id: int,
        equipment_data: EquipmentCreate,
        user_id: int
    ) -> Equipment:
        """
        Crée un équipement manuellement (admin/debug).
        """
        # Vérifier que le personnage existe et appartient à l'utilisateur
        character = await self._get_character_with_verification(character_id, user_id)

        # Créer l'équipement
        new_equipment = Equipment(
            character_id=character.id,
            name=equipment_data.name,
            description=equipment_data.description,
            slot=equipment_data.slot.value,
            rarity=equipment_data.rarity.value,
            stats=equipment_data.stats,
            sprite_key=equipment_data.sprite_key
        )

        self.db.add(new_equipment)
        await self.db.commit()
        await self.db.refresh(new_equipment)

        return new_equipment

    async def generate_equipment(
        self,
        character_id: int,
        user_id: int,
        slot: EquipmentSlot,
        rarity: EquipmentRarity,
        level: int = 1
    ) -> Equipment:
        """
        Génère un équipement aléatoire procédural.
        
        Stats générées selon:
        - Rareté: multiplicateur (Common 1.0 → Mythic 2.2)
        - Niveau: base pour les stats
        - Slot: détermine quelles stats privilégier
        """
        # Vérifier le personnage
        character = await self._get_character_with_verification(character_id, user_id)

        # Générer le nom
        name = self._generate_equipment_name(slot, rarity)

        # Générer la description
        description = self._generate_equipment_description(slot, rarity, level)

        # Générer les stats
        stats = self._generate_equipment_stats(slot, rarity, level)

        # Sprite key (format: slot_rarity_variant)
        variant = random.randint(1, 3)
        sprite_key = f"{slot.value}_{rarity.value}_{variant}"

        # Créer l'équipement
        new_equipment = Equipment(
            character_id=character.id,
            name=name,
            description=description,
            slot=slot.value,
            rarity=rarity.value,
            stats=stats,
            sprite_key=sprite_key
        )

        self.db.add(new_equipment)
        await self.db.commit()
        await self.db.refresh(new_equipment)

        return new_equipment

    async def get_equipment_by_id(
        self,
        equipment_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Equipment]:
        """Récupère un équipement par ID (avec vérification propriétaire optionnelle)"""
        result = await self.db.execute(
            select(Equipment).where(Equipment.id == equipment_id)
        )
        equipment = result.scalar_one_or_none()

        if equipment and user_id:
            # Vérifier que l'équipement appartient à un personnage du village de l'utilisateur
            character_result = await self.db.execute(
                select(Character).where(Character.id == equipment.character_id)
            )
            character = character_result.scalar_one_or_none()
            if not character:
                return None

            village_result = await self.db.execute(
                select(Village).where(
                    Village.id == character.village_id,
                    Village.user_id == user_id
                )
            )
            if not village_result.scalar_one_or_none():
                return None

        return equipment

    async def get_character_equipment(
        self,
        character_id: int,
        user_id: int
    ) -> List[Equipment]:
        """Récupère tous les équipements d'un personnage"""
        # Vérifier le personnage
        character = await self._get_character_with_verification(character_id, user_id)

        # Récupérer les équipements
        result = await self.db.execute(
            select(Equipment)
            .where(Equipment.character_id == character.id)
            .order_by(Equipment.obtained_at.desc())
        )
        return list(result.scalars().all())

    async def get_village_equipment(self, user_id: int) -> List[Equipment]:
        """Récupère tous les équipements du village (tous personnages)"""
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

        # Récupérer tous les personnages du village
        characters_result = await self.db.execute(
            select(Character).where(Character.village_id == village.id)
        )
        characters = list(characters_result.scalars().all())
        character_ids = [c.id for c in characters]

        # Récupérer tous les équipements
        result = await self.db.execute(
            select(Equipment)
            .where(Equipment.character_id.in_(character_ids))
            .order_by(Equipment.obtained_at.desc())
        )
        return list(result.scalars().all())

    async def equip_item(
        self,
        equipment_id: int,
        character_id: int,
        user_id: int
    ) -> Character:
        """
        Équipe un objet sur un personnage (met à jour equipment JSON du Character).
        Déséquipe automatiquement l'objet précédent dans ce slot.
        """
        # Vérifier l'équipement
        equipment = await self.get_equipment_by_id(equipment_id, user_id)
        if not equipment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Équipement non trouvé"
            )

        # Vérifier que l'équipement appartient bien au personnage
        if equipment.character_id != character_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cet équipement n'appartient pas à ce personnage"
            )

        # Récupérer le personnage
        character = await self._get_character_with_verification(character_id, user_id)

        # Mettre à jour l'équipement du personnage
        if not character.equipment:
            character.equipment = {}

        # Équiper dans le slot
        character.equipment[equipment.slot] = equipment.id

        await self.db.commit()
        await self.db.refresh(character)

        return character

    async def unequip_item(
        self,
        character_id: int,
        slot: EquipmentSlot,
        user_id: int
    ) -> Character:
        """Déséquipe un objet d'un slot spécifique"""
        # Récupérer le personnage
        character = await self._get_character_with_verification(character_id, user_id)

        # Vérifier que le slot est équipé
        if not character.equipment or slot.value not in character.equipment:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Aucun équipement dans le slot {slot.value}"
            )

        # Déséquiper
        del character.equipment[slot.value]

        await self.db.commit()
        await self.db.refresh(character)

        return character

    async def transfer_equipment(
        self,
        equipment_id: int,
        from_character_id: int,
        to_character_id: int,
        user_id: int
    ) -> Equipment:
        """
        Transfère un équipement d'un personnage à un autre (même village).
        Déséquipe automatiquement si équipé.
        """
        # Vérifier l'équipement
        equipment = await self.get_equipment_by_id(equipment_id, user_id)
        if not equipment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Équipement non trouvé"
            )

        if equipment.character_id != from_character_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="L'équipement n'appartient pas au personnage source"
            )

        # Vérifier les deux personnages
        from_char = await self._get_character_with_verification(from_character_id, user_id)
        to_char = await self._get_character_with_verification(to_character_id, user_id)

        # Déséquiper si équipé
        if from_char.equipment and equipment.slot in from_char.equipment:
            if from_char.equipment[equipment.slot] == equipment.id:
                del from_char.equipment[equipment.slot]

        # Transférer
        equipment.character_id = to_character_id

        await self.db.commit()
        await self.db.refresh(equipment)

        return equipment

    async def delete_equipment(
        self,
        equipment_id: int,
        user_id: int
    ) -> bool:
        """
        Supprime un équipement (destruction/vente).
        Déséquipe automatiquement si équipé.
        """
        # Vérifier l'équipement
        equipment = await self.get_equipment_by_id(equipment_id, user_id)
        if not equipment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Équipement non trouvé"
            )

        # Déséquiper si équipé
        character_result = await self.db.execute(
            select(Character).where(Character.id == equipment.character_id)
        )
        character = character_result.scalar_one_or_none()
        if character and character.equipment:
            if equipment.slot in character.equipment:
                if character.equipment[equipment.slot] == equipment.id:
                    del character.equipment[equipment.slot]

        # Supprimer
        await self.db.delete(equipment)
        await self.db.commit()

        return True

    async def calculate_total_stats(self, character_id: int, user_id: int) -> Dict[str, int]:
        """
        Calcule les stats totales d'un personnage (base + équipement).
        """
        # Récupérer le personnage
        character = await self._get_character_with_verification(character_id, user_id)

        # Stats de base
        total_stats = {
            "strength": character.strength,
            "dexterity": character.dexterity,
            "endurance": character.endurance,
            "intelligence": character.intelligence,
            "speed": character.speed,
            "luck": character.luck,
            "armor": 0,
            "damage": 0
        }

        # Ajouter bonus équipement
        if character.equipment:
            for slot, equipment_id in character.equipment.items():
                equipment_result = await self.db.execute(
                    select(Equipment).where(Equipment.id == equipment_id)
                )
                equipment = equipment_result.scalar_one_or_none()
                
                if equipment:
                    for stat, value in equipment.stats.items():
                        if stat in total_stats:
                            total_stats[stat] += value

        return total_stats

    # ============================================================================
    # MÉTHODES PRIVÉES - GÉNÉRATION PROCÉDURALE
    # ============================================================================

    def _generate_equipment_name(self, slot: EquipmentSlot, rarity: EquipmentRarity) -> str:
        """Génère un nom d'équipement aléatoire"""
        # Préfixes par rareté
        prefixes = {
            EquipmentRarity.COMMON: ["Simple", "Basique", "Ordinaire", "Standard"],
            EquipmentRarity.UNCOMMON: ["Renforcé", "Amélioré", "Solide", "Robuste"],
            EquipmentRarity.RARE: ["Supérieur", "Exceptionnel", "Remarquable", "Distingué"],
            EquipmentRarity.EPIC: ["Épique", "Héroïque", "Légendaire", "Glorieux"],
            EquipmentRarity.LEGENDARY: ["Mythique", "Ancestral", "Divin", "Éternel"],
            EquipmentRarity.MYTHIC: ["Céleste", "Transcendant", "Cosmique", "Ultime"]
        }

        # Noms de base par slot
        base_names = {
            EquipmentSlot.HEAD: ["Casque", "Heaume", "Couronne", "Bandeau"],
            EquipmentSlot.SHOULDERS: ["Épaulières", "Protections d'épaules", "Manteau"],
            EquipmentSlot.TORSO: ["Armure", "Plastron", "Tunique", "Haubert"],
            EquipmentSlot.LEGS: ["Jambières", "Pantalon", "Cuissardes"],
            EquipmentSlot.FEET: ["Bottes", "Chaussures", "Sandales"],
            EquipmentSlot.HANDS: ["Gants", "Gantelets", "Mitaines"],
            EquipmentSlot.JEWELRY_1: ["Anneau", "Bague", "Amulette"],
            EquipmentSlot.JEWELRY_2: ["Collier", "Pendentif", "Talisman"],
            EquipmentSlot.JEWELRY_3: ["Bracelet", "Médaillon", "Charm"],
            EquipmentSlot.WEAPON_1: ["Épée", "Hache", "Lance", "Marteau"],
            EquipmentSlot.WEAPON_2: ["Bouclier", "Dague", "Épée courte"]
        }

        prefix = random.choice(prefixes.get(rarity, ["Simple"]))
        base = random.choice(base_names.get(slot, ["Objet"]))

        # Suffixes occasionnels pour rareté élevée
        if rarity in [EquipmentRarity.EPIC, EquipmentRarity.LEGENDARY, EquipmentRarity.MYTHIC]:
            suffixes = ["du Titan", "du Phénix", "de l'Ombre", "de la Tempête", "du Dragon"]
            if random.random() < 0.5:
                return f"{prefix} {base} {random.choice(suffixes)}"

        return f"{prefix} {base}"

    def _generate_equipment_description(self, slot: EquipmentSlot, rarity: EquipmentRarity, level: int) -> str:
        """Génère une description aléatoire"""
        descriptions = {
            EquipmentRarity.COMMON: "Un équipement simple mais fonctionnel.",
            EquipmentRarity.UNCOMMON: "Un équipement de qualité correcte, renforcé pour durer.",
            EquipmentRarity.RARE: "Un équipement exceptionnel, forgé avec soin.",
            EquipmentRarity.EPIC: "Un équipement épique, imprégné d'une puissance remarquable.",
            EquipmentRarity.LEGENDARY: "Un équipement légendaire, digne des plus grands héros.",
            EquipmentRarity.MYTHIC: "Un équipement mythique, tissé des fils du destin lui-même."
        }
        
        base_desc = descriptions.get(rarity, "Un équipement.")
        return f"{base_desc} Niveau recommandé: {level}."

    def _generate_equipment_stats(self, slot: EquipmentSlot, rarity: EquipmentRarity, level: int) -> Dict[str, int]:
        """Génère les stats d'un équipement"""
        stats = {
            "strength": 0,
            "dexterity": 0,
            "endurance": 0,
            "intelligence": 0,
            "speed": 0,
            "luck": 0,
            "armor": 0,
            "damage": 0
        }

        # Multiplicateur de rareté
        rarity_mult = RARITY_MULTIPLIERS.get(rarity, 1.0)

        # Budget de stats selon niveau et rareté
        budget = int(level * 2 * rarity_mult)

        # Stats principales selon le slot
        primary_stats = self._get_primary_stats_for_slot(slot)

        # Distribuer le budget
        remaining_budget = budget
        for stat in primary_stats:
            if remaining_budget <= 0:
                break
            
            # 40-70% du budget restant pour chaque stat principale
            allocation = int(remaining_budget * random.uniform(0.4, 0.7))
            stats[stat] = max(1, allocation)
            remaining_budget -= allocation

        # Distribuer le reste aléatoirement
        while remaining_budget > 0:
            random_stat = random.choice(list(stats.keys()))
            stats[random_stat] += 1
            remaining_budget -= 1

        return stats

    def _get_primary_stats_for_slot(self, slot: EquipmentSlot) -> List[str]:
        """Détermine les stats principales selon le slot"""
        slot_stats = {
            EquipmentSlot.HEAD: ["endurance", "intelligence", "armor"],
            EquipmentSlot.SHOULDERS: ["endurance", "armor"],
            EquipmentSlot.TORSO: ["endurance", "armor"],
            EquipmentSlot.LEGS: ["endurance", "speed", "armor"],
            EquipmentSlot.FEET: ["speed", "dexterity"],
            EquipmentSlot.HANDS: ["strength", "dexterity", "damage"],
            EquipmentSlot.JEWELRY_1: ["luck", "intelligence"],
            EquipmentSlot.JEWELRY_2: ["luck", "endurance"],
            EquipmentSlot.JEWELRY_3: ["luck", "speed"],
            EquipmentSlot.WEAPON_1: ["strength", "damage"],
            EquipmentSlot.WEAPON_2: ["armor", "endurance"]
        }
        return slot_stats.get(slot, ["strength"])

    async def _get_character_with_verification(self, character_id: int, user_id: int) -> Character:
        """Récupère un personnage avec vérification d'appartenance au village"""
        character_result = await self.db.execute(
            select(Character).where(Character.id == character_id)
        )
        character = character_result.scalar_one_or_none()
        
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Personnage non trouvé"
            )

        # Vérifier appartenance au village
        village_result = await self.db.execute(
            select(Village).where(
                Village.id == character.village_id,
                Village.user_id == user_id
            )
        )
        if not village_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Ce personnage n'appartient pas à votre village"
            )

        return character
