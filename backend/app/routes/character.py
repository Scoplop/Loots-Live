"""
Routes API pour la gestion des personnages.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.user import User
from backend.app.schemas.character import (
    CharacterCreate,
    CharacterCreateAI,
    CharacterResponse,
    CharacterUpdate,
    CharacterAllocateStats,
    CharacterStats
)
from backend.app.services.character_service import CharacterService
from backend.app.utils.dependencies import get_current_active_user


router = APIRouter(prefix="/characters", tags=["characters"])


@router.post("/", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_player_character(
    character_data: CharacterCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Crée le personnage joueur (obligatoire après inscription).
    Un joueur ne peut créer qu'UN SEUL personnage joueur.
    
    - **name**: Nom du personnage (1-50 caractères)
    - **character_class**: Classe (warrior, scout, craftsman, leader, survivor)
    - **sex**: Sexe (male, female, non_binary)
    - **strength, dexterity, endurance, intelligence, speed, luck**: Allocation stats (max 10 points libres + bonus classe)
    - **biography**: Optionnel, histoire du personnage
    - **appearance**: Optionnel, apparence personnalisée
    """
    service = CharacterService(db)
    character = await service.create_player_character(current_user.id, character_data)
    return character


@router.post("/ai", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_ai_character(
    character_data: CharacterCreateAI,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Crée un PNJ IA pour le village.
    Stats générées aléatoirement (0-5 par stat + bonus classe).
    
    - **name**: Nom du PNJ
    - **character_class**: Classe
    - **personality**: Personnalité (friendly, shy, authoritarian, wise, jovial, methodical, adventurer, maternal, grumpy, mysterious)
    - **sex**: Sexe
    - **biography**: Optionnel
    - **appearance**: Optionnel (sinon aléatoire)
    """
    service = CharacterService(db)
    character = await service.create_ai_character(current_user.id, character_data)
    return character


@router.get("/me", response_model=CharacterResponse)
async def get_my_player_character(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère le personnage joueur de l'utilisateur connecté.
    """
    service = CharacterService(db)
    character = await service.get_player_character(current_user.id)
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vous n'avez pas encore créé votre personnage joueur"
        )
    
    return character


@router.get("/", response_model=List[CharacterResponse])
async def get_all_village_characters(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère tous les personnages du village (joueur + PNJ IA).
    Triés par: joueur d'abord, puis alphabétique.
    """
    service = CharacterService(db)
    characters = await service.get_all_village_characters(current_user.id)
    return characters


@router.get("/ai", response_model=List[CharacterResponse])
async def get_ai_characters_only(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère uniquement les PNJ IA du village.
    """
    service = CharacterService(db)
    characters = await service.get_ai_characters(current_user.id)
    return characters


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character_details(
    character_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère les détails d'un personnage spécifique.
    Doit appartenir au village de l'utilisateur.
    """
    service = CharacterService(db)
    character = await service.get_character_by_id(character_id, current_user.id)
    
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personnage non trouvé"
        )
    
    return character


@router.get("/{character_id}/stats", response_model=CharacterStats)
async def get_character_full_stats(
    character_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère les statistiques complètes d'un personnage.
    Inclut stats de base, stats avec équipement, HP, niveau, XP, bonus classe.
    """
    service = CharacterService(db)
    
    # Vérifier que le personnage appartient à l'utilisateur
    character = await service.get_character_by_id(character_id, current_user.id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personnage non trouvé"
        )
    
    stats = await service.get_character_stats(character_id)
    return stats


@router.put("/{character_id}", response_model=CharacterResponse)
async def update_character_info(
    character_id: int,
    character_data: CharacterUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Met à jour les informations d'un personnage (nom, bio, apparence).
    Ne permet PAS de modifier les stats ou la classe.
    """
    service = CharacterService(db)
    character = await service.update_character(character_id, current_user.id, character_data)
    return character


@router.post("/{character_id}/allocate-stats", response_model=CharacterResponse)
async def allocate_character_stats(
    character_id: int,
    stats_data: CharacterAllocateStats,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Alloue les points de stats libres du personnage joueur.
    Uniquement disponible pour le PNJ joueur (pas les PNJ IA).
    
    - **strength, dexterity, endurance, intelligence, speed, luck**: Points à allouer
    - Total ne doit pas dépasser free_stat_points disponibles
    """
    service = CharacterService(db)
    character = await service.allocate_stats(character_id, current_user.id, stats_data)
    return character


@router.post("/{character_id}/heal", response_model=CharacterResponse)
async def heal_character(
    character_id: int,
    heal_amount: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Soigne un personnage (debug/admin).
    
    - **heal_amount**: Montant de HP à restaurer (ne peut dépasser max_hp)
    """
    service = CharacterService(db)
    
    # Vérifier appartenance
    character = await service.get_character_by_id(character_id, current_user.id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personnage non trouvé"
        )
    
    character = await service.heal_character(character_id, heal_amount)
    return character


@router.post("/{character_id}/damage", response_model=CharacterResponse)
async def damage_character(
    character_id: int,
    damage_amount: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Inflige des dégâts à un personnage (debug/admin).
    
    - **damage_amount**: Montant de dégâts (peut tomber à 0 HP)
    """
    service = CharacterService(db)
    
    # Vérifier appartenance
    character = await service.get_character_by_id(character_id, current_user.id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personnage non trouvé"
        )
    
    character = await service.damage_character(character_id, damage_amount)
    return character


@router.post("/{character_id}/gain-xp", response_model=CharacterResponse)
async def gain_character_xp(
    character_id: int,
    xp_amount: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Donne de l'XP à un personnage (debug/admin).
    Gère automatiquement les montées de niveau.
    
    - **xp_amount**: Montant d'XP à ajouter
    """
    service = CharacterService(db)
    
    # Vérifier appartenance
    character = await service.get_character_by_id(character_id, current_user.id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Personnage non trouvé"
        )
    
    character = await service.gain_xp(character_id, xp_amount)
    return character


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ai_character(
    character_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Supprime un PNJ IA.
    IMPOSSIBLE de supprimer le personnage joueur.
    IMPOSSIBLE de supprimer un PNJ en mission.
    """
    service = CharacterService(db)
    await service.delete_character(character_id, current_user.id)
    return None
