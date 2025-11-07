"""
Routes API pour les recherches (arbre technologique).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID

from backend.app.database import get_db
from backend.app.utils.dependencies import get_current_active_user
from backend.app.models.user import User
from backend.app.services.research_service import ResearchService
from backend.app.services.village_service import VillageService
from backend.app.schemas.research import (
    ResearchRead,
    ResearchTree,
    ResearchDetails,
    ResearchBonuses
)
from backend.app.utils.constants import ResearchCategory, ResearchStatus


router = APIRouter(prefix="/researches", tags=["researches"])


@router.post("/initialize", response_model=List[ResearchRead])
async def initialize_village_researches(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Initialise toutes les recherches pour le village de l'utilisateur.
    À appeler après la création du village.
    """
    village_service = VillageService(db)
    village = await village_service.get_user_village(current_user.id)
    
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun village trouvé pour cet utilisateur"
        )
    
    research_service = ResearchService(db)
    researches = await research_service.initialize_village_researches(village.id)
    
    return researches


@router.get("/tree", response_model=ResearchTree)
async def get_tech_tree(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère l'arbre technologique complet du village.
    Organisé par catégories avec statuts et progression.
    """
    village_service = VillageService(db)
    village = await village_service.get_user_village(current_user.id)
    
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun village trouvé"
        )
    
    research_service = ResearchService(db)
    tree = await research_service.get_tech_tree(village.id)
    
    return tree


@router.get("/available", response_model=List[ResearchDetails])
async def get_available_researches(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère toutes les recherches AVAILABLE (débloquées mais pas commencées).
    """
    village_service = VillageService(db)
    village = await village_service.get_user_village(current_user.id)
    
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun village trouvé"
        )
    
    research_service = ResearchService(db)
    available = await research_service.get_available_researches(village.id)
    
    return available


@router.get("", response_model=List[ResearchRead])
async def list_researches(
    status_filter: Optional[ResearchStatus] = None,
    category: Optional[ResearchCategory] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Liste toutes les recherches du village avec filtres optionnels.
    """
    village_service = VillageService(db)
    village = await village_service.get_user_village(current_user.id)
    
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun village trouvé"
        )
    
    research_service = ResearchService(db)
    researches = await research_service.get_village_researches(
        village_id=village.id,
        status=status_filter,
        category=category
    )
    
    return researches


@router.get("/{research_id}", response_model=ResearchDetails)
async def get_research_details(
    research_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère les détails complets d'une recherche.
    """
    research_service = ResearchService(db)
    research = await research_service.get_research(research_id)
    
    if not research:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recherche introuvable"
        )
    
    # Vérifier que la recherche appartient au village de l'utilisateur
    village_service = VillageService(db)
    village = await village_service.get_user_village(current_user.id)
    
    if not village or research.village_id != village.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cette recherche n'appartient pas à votre village"
        )
    
    # Récupérer les détails depuis RESEARCH_TREE
    details = await research_service.get_research_details(research.research_key)
    
    return {
        "id": research.id,
        "research_key": research.research_key,
        "category": research.category,
        "status": research.status,
        "progress": research.progress,
        "started_at": research.started_at,
        "completed_at": research.completed_at,
        **details
    }


@router.post("/{research_key}/start", response_model=ResearchRead)
async def start_research(
    research_key: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Démarre une recherche.
    Vérifie les prérequis et consomme les ressources.
    """
    village_service = VillageService(db)
    village = await village_service.get_user_village(current_user.id)
    
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun village trouvé"
        )
    
    research_service = ResearchService(db)
    research, error = await research_service.start_research(village.id, research_key)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return research


@router.post("/{research_id}/complete", response_model=ResearchRead)
async def complete_research(
    research_id: UUID,
    force: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Complète une recherche.
    Si force=False, vérifie que la durée est écoulée.
    Si force=True, complète immédiatement (admin/workers).
    """
    research_service = ResearchService(db)
    research = await research_service.get_research(research_id)
    
    if not research:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recherche introuvable"
        )
    
    # Vérifier que la recherche appartient au village de l'utilisateur
    village_service = VillageService(db)
    village = await village_service.get_user_village(current_user.id)
    
    if not village or research.village_id != village.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cette recherche n'appartient pas à votre village"
        )
    
    completed_research, error = await research_service.complete_research(research_id, force)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return completed_research


@router.post("/{research_id}/cancel", response_model=ResearchRead)
async def cancel_research(
    research_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Annule une recherche en cours.
    Ne rembourse PAS les ressources déjà consommées.
    """
    research_service = ResearchService(db)
    research = await research_service.get_research(research_id)
    
    if not research:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recherche introuvable"
        )
    
    # Vérifier que la recherche appartient au village de l'utilisateur
    village_service = VillageService(db)
    village = await village_service.get_user_village(current_user.id)
    
    if not village or research.village_id != village.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cette recherche n'appartient pas à votre village"
        )
    
    cancelled, error = await research_service.cancel_research(research_id)
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return cancelled


@router.get("/bonuses/active", response_model=ResearchBonuses)
async def get_active_bonuses(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère tous les bonus actifs des recherches complétées.
    """
    village_service = VillageService(db)
    village = await village_service.get_user_village(current_user.id)
    
    if not village:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun village trouvé"
        )
    
    research_service = ResearchService(db)
    bonuses = await research_service.get_research_bonuses(village.id)
    
    return bonuses
