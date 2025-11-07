"""
Routes API pour la gestion des missions.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from backend.app.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.user import User
from backend.app.schemas.mission import (
    MissionCreate,
    MissionResponse,
    MissionComplete
)
from backend.app.services.mission_service import MissionService
from backend.app.utils.dependencies import get_current_active_user
from backend.app.utils.constants import MissionType, MissionStatus


router = APIRouter(prefix="/missions", tags=["missions"])


@router.post("/", response_model=MissionResponse, status_code=status.HTTP_201_CREATED)
async def create_mission(
    mission_data: MissionCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Crée une nouvelle mission (état: PREPARING).
    
    - **name**: Nom de la mission
    - **description**: Description
    - **mission_type**: Type (harvest, rescue, exploration)
    - **difficulty**: Difficulté 1-10
    - **duration_minutes**: Durée en minutes (5-1440)
    - **rewards**: Récompenses JSON (resources, xp, equipment_chance)
    - **participant_ids**: Liste des PNJ participants (2-5)
    
    Vérifie:
    - Participants appartiennent au village
    - PNJ non déjà en mission
    - PNJ avec HP > 0
    - Nombre participants 2-5
    
    La mission n'est pas encore lancée. Utilisez /start pour la démarrer.
    """
    service = MissionService(db)
    mission = await service.create_mission(current_user.id, mission_data)
    return mission


@router.post("/{mission_id}/start", response_model=MissionResponse)
async def start_mission(
    mission_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Lance une mission (PREPARING → IN_PROGRESS).
    
    - **mission_id**: ID de la mission à lancer
    
    Actions:
    - Marque les participants comme en mission
    - Enregistre heure de départ
    - Change statut à IN_PROGRESS
    
    En production, un worker termine automatiquement la mission après duration_minutes.
    """
    service = MissionService(db)
    mission = await service.start_mission(mission_id, current_user.id)
    return mission


@router.post("/{mission_id}/complete", response_model=MissionComplete)
async def complete_mission(
    mission_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Termine une mission manuellement et calcule les résultats.
    
    - **mission_id**: ID de la mission à terminer
    
    Calcule:
    - Taux de réussite basé sur stats équipe, difficulté, bonus/malus
    - Récompenses complètes si succès, 30% si échec
    - XP distribuée aux participants
    - Casualties (30% chance blessure si échec)
    
    Retourne:
    - success: true/false
    - rewards_obtained: ressources gagnées
    - casualties: liste PNJ blessés
    - xp_gained: XP par participant
    
    Note: En production, un worker appelle cette méthode automatiquement.
    """
    service = MissionService(db)
    result = await service.complete_mission(mission_id, current_user.id)
    return result


@router.post("/{mission_id}/recall", response_model=MissionResponse)
async def recall_mission(
    mission_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Rappelle une mission en cours (annulation).
    
    - **mission_id**: ID de la mission à rappeler
    
    Résultats:
    - Mission marquée RECALLED
    - PNJ rentrent au village sans dégâts
    - Aucune récompense
    
    Utile pour sauver une équipe en danger ou libérer des PNJ.
    """
    service = MissionService(db)
    mission = await service.recall_mission(mission_id, current_user.id)
    return mission


@router.get("/", response_model=List[MissionResponse])
async def get_my_missions(
    status_filter: Optional[MissionStatus] = Query(None, description="Filtrer par statut"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère toutes les missions du village.
    
    - **status**: Filtre optionnel (preparing, in_progress, completed, failed, recalled)
    
    Retourne la liste triée par date (plus récent d'abord).
    """
    service = MissionService(db)
    missions = await service.get_village_missions(current_user.id, status_filter)
    return missions


@router.get("/{mission_id}", response_model=MissionResponse)
async def get_mission_details(
    mission_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Récupère les détails d'une mission spécifique.
    
    - **mission_id**: ID de la mission
    
    Inclut participants, récompenses, statut, dates.
    """
    service = MissionService(db)
    mission = await service.get_mission_by_id(mission_id, current_user.id)
    
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission non trouvée"
        )
    
    return mission


@router.get("/{mission_id}/success-rate", response_model=dict)
async def calculate_mission_success_rate(
    mission_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Calcule le taux de réussite estimé d'une mission.
    
    - **mission_id**: ID de la mission
    
    Formule:
    - Score équipe = Σ(stats_PNJ) / nb_participants
    - Taux base = min(0.9, Score / (difficulté × 50))
    - Bonus Leader: +5%
    - Malus moral village < 50: -10%
    
    Retourne:
    - success_rate: Probabilité de réussite (0.1-0.95)
    - team_power: Puissance totale de l'équipe
    - required_power: Puissance requise pour la mission
    """
    service = MissionService(db)
    
    # Vérifier que la mission existe et appartient à l'utilisateur
    mission = await service.get_mission_by_id(mission_id, current_user.id)
    if not mission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mission non trouvée"
        )
    
    success_rate = await service.calculate_success_rate(mission_id)
    
    return {
        "success_rate": round(success_rate, 2),
        "success_percentage": f"{round(success_rate * 100)}%",
        "difficulty": mission.difficulty,
        "recommended_power": mission.difficulty * 50
    }


@router.delete("/{mission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mission(
    mission_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Supprime une mission.
    
    - **mission_id**: ID de la mission à supprimer
    
    Conditions:
    - Mission doit être PREPARING ou terminée (COMPLETED/FAILED/RECALLED)
    - Impossible de supprimer une mission IN_PROGRESS (utilisez /recall)
    
    Supprime aussi les participants associés (cascade).
    """
    service = MissionService(db)
    await service.delete_mission(mission_id, current_user.id)
    return None


@router.get("/generate/{mission_type}", response_model=dict)
async def generate_random_mission(
    mission_type: MissionType,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Génère une proposition de mission aléatoire.
    
    - **mission_type**: Type de mission (harvest, rescue, exploration)
    
    Retourne:
    - name: Nom généré
    - description: Description
    - difficulty: Difficulté aléatoire 1-10
    - duration_minutes: Durée selon type
    - rewards: Ressources, XP, chance équipement
    
    Utile pour générer des missions procédurales.
    Utilisez POST / avec ces paramètres + participant_ids pour créer la mission.
    """
    service = MissionService(db)
    mission_proposal = await service.generate_random_mission(current_user.id, mission_type)
    return mission_proposal
