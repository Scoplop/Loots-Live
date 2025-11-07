"""
Routes API pour la gestion des équipements.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query

from backend.app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.user import User
from backend.app.schemas.equipment import (
    EquipmentCreate,
    EquipmentResponse,
    EquipmentGenerate
)
from backend.app.services.equipment_service import EquipmentService
from backend.app.utils.dependencies import get_current_active_user
from backend.app.utils.constants import EquipmentSlot, EquipmentRarity


router = APIRouter(prefix="/equipment", tags=["equipment"])


@router.post("/", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
async def create_equipment(
    character_id: int,
    equipment_data: EquipmentCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Crée un équipement manuellement (admin/debug).
    
    - **character_id**: ID du personnage propriétaire
    - **equipment_data**: Données complètes de l'équipement
    
    Nécessite de spécifier tous les champs (nom, description, slot, rareté, stats, sprite).
    Pour génération procédurale, utilisez POST /generate.
    """
    service = EquipmentService(db)
    equipment = await service.create_equipment(character_id, equipment_data, current_user.id)
    return equipment


@router.post("/generate", response_model=EquipmentResponse, status_code=status.HTTP_201_CREATED)
async def generate_equipment(
    character_id: int,
    slot: EquipmentSlot = Query(..., description="Slot de l'équipement"),
    rarity: EquipmentRarity = Query(..., description="Rareté de l'équipement"),
    level: int = Query(1, ge=1, le=100, description="Niveau recommandé"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Génère un équipement aléatoire procédural.
    
    - **character_id**: ID du personnage qui reçoit l'équipement
    - **slot**: Slot (head, torso, weapon_1, etc.)
    - **rarity**: Rareté (common, uncommon, rare, epic, legendary, mythic)
    - **level**: Niveau recommandé (1-100) - affecte les stats
    
    Génère automatiquement:
    - Nom thématique selon rareté et slot
    - Description
    - Stats optimisées pour le slot
    - Sprite key
    
    Formule stats:
    - Budget = niveau × 2 × multiplicateur_rareté
    - Common: ×1.0, Uncommon: ×1.15, Rare: ×1.30, Epic: ×1.50, Legendary: ×1.80, Mythic: ×2.20
    """
    service = EquipmentService(db)
    equipment = await service.generate_equipment(
        character_id,
        current_user.id,
        slot,
        rarity,
        level
    )
    return equipment


@router.get("/character/{character_id}", response_model=List[EquipmentResponse])
async def get_character_equipment(
    character_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère tous les équipements d'un personnage.
    
    - **character_id**: ID du personnage
    
    Retourne la liste triée par date d'obtention (plus récent d'abord).
    """
    service = EquipmentService(db)
    equipment_list = await service.get_character_equipment(character_id, current_user.id)
    return equipment_list


@router.get("/village", response_model=List[EquipmentResponse])
async def get_village_equipment(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère tous les équipements du village (tous personnages).
    
    Utile pour:
    - Vue d'ensemble de l'armurerie
    - Gestion centralisée
    - Statistiques
    """
    service = EquipmentService(db)
    equipment_list = await service.get_village_equipment(current_user.id)
    return equipment_list


@router.get("/{equipment_id}", response_model=EquipmentResponse)
async def get_equipment_details(
    equipment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère les détails d'un équipement spécifique.
    
    - **equipment_id**: ID de l'équipement
    """
    service = EquipmentService(db)
    equipment = await service.get_equipment_by_id(equipment_id, current_user.id)
    
    if not equipment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Équipement non trouvé"
        )
    
    return equipment


@router.post("/{equipment_id}/equip", response_model=dict)
async def equip_item(
    equipment_id: int,
    character_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Équipe un objet sur un personnage.
    
    - **equipment_id**: ID de l'équipement à équiper
    - **character_id**: ID du personnage
    
    Actions:
    - Déséquipe automatiquement l'objet précédent dans ce slot
    - Met à jour le JSON equipment du personnage
    - Applique les bonus stats
    
    L'équipement doit appartenir au personnage.
    """
    service = EquipmentService(db)
    character = await service.equip_item(equipment_id, character_id, current_user.id)
    
    return {
        "message": "Équipement équipé avec succès",
        "character_id": character.id,
        "equipped_items": character.equipment
    }


@router.post("/{character_id}/unequip/{slot}", response_model=dict)
async def unequip_item(
    character_id: int,
    slot: EquipmentSlot,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Déséquipe un objet d'un slot spécifique.
    
    - **character_id**: ID du personnage
    - **slot**: Slot à libérer
    
    L'objet reste dans l'inventaire du personnage, juste déséquipé.
    """
    service = EquipmentService(db)
    character = await service.unequip_item(character_id, slot, current_user.id)
    
    return {
        "message": f"Slot {slot.value} déséquipé",
        "character_id": character.id,
        "equipped_items": character.equipment
    }


@router.post("/{equipment_id}/transfer", response_model=EquipmentResponse)
async def transfer_equipment(
    equipment_id: int,
    from_character_id: int,
    to_character_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Transfère un équipement d'un personnage à un autre (même village).
    
    - **equipment_id**: ID de l'équipement
    - **from_character_id**: ID du personnage source
    - **to_character_id**: ID du personnage cible
    
    Déséquipe automatiquement si l'objet était équipé.
    Les deux personnages doivent appartenir au même village.
    """
    service = EquipmentService(db)
    equipment = await service.transfer_equipment(
        equipment_id,
        from_character_id,
        to_character_id,
        current_user.id
    )
    return equipment


@router.delete("/{equipment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_equipment(
    equipment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Supprime un équipement (destruction/vente).
    
    - **equipment_id**: ID de l'équipement à supprimer
    
    Déséquipe automatiquement si équipé.
    Action irréversible.
    """
    service = EquipmentService(db)
    await service.delete_equipment(equipment_id, current_user.id)
    return None


@router.get("/character/{character_id}/total-stats", response_model=dict)
async def get_character_total_stats(
    character_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calcule les stats totales d'un personnage (base + équipement).
    
    - **character_id**: ID du personnage
    
    Retourne:
    - strength, dexterity, endurance, intelligence, speed, luck: Stats combinées
    - armor: Armure totale (équipement uniquement)
    - damage: Dégâts totaux (équipement uniquement)
    
    Prend en compte tous les objets équipés.
    """
    service = EquipmentService(db)
    total_stats = await service.calculate_total_stats(character_id, current_user.id)
    
    return {
        "character_id": character_id,
        "total_stats": total_stats
    }
