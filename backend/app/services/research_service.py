"""
Service de gestion des recherches (arbre technologique).
Gère les prérequis, les coûts, les débloquages et la progression.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from backend.app.models.research import Research, ResearchStatus
from backend.app.models.village import Village
from backend.app.services.village_service import VillageService
from backend.app.utils.constants import (
    RESEARCH_TREE,
    ResearchCategory
)


class ResearchService:
    """Service pour gérer les recherches technologiques."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.village_service = VillageService(db)
    
    async def get_research(self, research_id: UUID) -> Optional[Research]:
        """Récupère une recherche par son ID."""
        result = await self.db.execute(
            select(Research).where(Research.id == research_id)
        )
        return result.scalar_one_or_none()
    
    async def get_village_researches(
        self,
        village_id: UUID,
        status: Optional[ResearchStatus] = None,
        category: Optional[ResearchCategory] = None
    ) -> List[Research]:
        """Récupère toutes les recherches d'un village avec filtres optionnels."""
        query = select(Research).where(Research.village_id == village_id)
        
        if status:
            query = query.where(Research.status == status)
        if category:
            query = query.where(Research.category == category)
        
        query = query.order_by(Research.category, Research.research_key)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def initialize_village_researches(self, village_id: UUID) -> List[Research]:
        """
        Initialise toutes les recherches disponibles pour un nouveau village.
        Toutes commencent LOCKED sauf celles sans prérequis (AVAILABLE).
        """
        researches = []
        
        for key, data in RESEARCH_TREE.items():
            # Déterminer le statut initial
            status = ResearchStatus.AVAILABLE if not data.get("prerequisites") else ResearchStatus.LOCKED
            
            research = Research(
                village_id=village_id,
                research_key=key,
                category=data["category"],
                status=status,
                progress=0,
                started_at=None,
                completed_at=None
            )
            self.db.add(research)
            researches.append(research)
        
        await self.db.commit()
        return researches
    
    async def get_research_details(self, research_key: str) -> Dict[str, Any]:
        """Récupère les détails complets d'une recherche depuis RESEARCH_TREE."""
        if research_key not in RESEARCH_TREE:
            return {}
        
        data = RESEARCH_TREE[research_key].copy()
        return data
    
    async def get_available_researches(self, village_id: UUID) -> List[Dict[str, Any]]:
        """
        Récupère toutes les recherches disponibles (AVAILABLE) pour un village.
        Retourne les détails complets avec coûts et bénéfices.
        """
        researches = await self.get_village_researches(
            village_id=village_id,
            status=ResearchStatus.AVAILABLE
        )
        
        detailed = []
        for research in researches:
            details = await self.get_research_details(research.research_key)
            detailed.append({
                "id": research.id,
                "research_key": research.research_key,
                "category": research.category,
                "status": research.status,
                **details
            })
        
        return detailed
    
    async def check_prerequisites(
        self,
        village_id: UUID,
        research_key: str
    ) -> tuple[bool, List[str]]:
        """
        Vérifie si tous les prérequis d'une recherche sont complétés.
        Retourne (succès, liste des prérequis manquants).
        """
        data = RESEARCH_TREE.get(research_key)
        if not data:
            return False, ["Recherche introuvable"]
        
        prerequisites = data.get("prerequisites", [])
        if not prerequisites:
            return True, []
        
        # Récupérer toutes les recherches complétées du village
        completed = await self.get_village_researches(
            village_id=village_id,
            status=ResearchStatus.COMPLETED
        )
        completed_keys = [r.research_key for r in completed]
        
        # Vérifier chaque prérequis
        missing = []
        for prereq in prerequisites:
            if prereq not in completed_keys:
                missing.append(prereq)
        
        return len(missing) == 0, missing
    
    async def can_afford_research(
        self,
        village_id: UUID,
        research_key: str
    ) -> tuple[bool, Dict[str, int]]:
        """
        Vérifie si le village a les ressources nécessaires.
        Retourne (peut payer, ressources manquantes).
        """
        data = RESEARCH_TREE.get(research_key)
        if not data:
            return False, {}
        
        village = await self.village_service.get_village(village_id)
        if not village:
            return False, {}
        
        costs = data.get("costs", {})
        missing = {}
        
        for resource, amount in costs.items():
            current = getattr(village, resource, 0)
            if current < amount:
                missing[resource] = amount - current
        
        return len(missing) == 0, missing
    
    async def start_research(
        self,
        village_id: UUID,
        research_key: str
    ) -> tuple[Optional[Research], Optional[str]]:
        """
        Démarre une recherche si les conditions sont remplies.
        Retourne (recherche, message d'erreur si échec).
        """
        # Vérifier qu'il n'y a pas déjà une recherche en cours
        in_progress = await self.get_village_researches(
            village_id=village_id,
            status=ResearchStatus.IN_PROGRESS
        )
        if in_progress:
            return None, "Une recherche est déjà en cours"
        
        # Récupérer la recherche
        result = await self.db.execute(
            select(Research).where(
                Research.village_id == village_id,
                Research.research_key == research_key
            )
        )
        research = result.scalar_one_or_none()
        
        if not research:
            return None, "Recherche introuvable"
        
        if research.status == ResearchStatus.COMPLETED:
            return None, "Recherche déjà complétée"
        
        if research.status == ResearchStatus.LOCKED:
            return None, "Recherche verrouillée (prérequis manquants)"
        
        # Vérifier les prérequis (double check)
        can_start, missing_prereqs = await self.check_prerequisites(village_id, research_key)
        if not can_start:
            return None, f"Prérequis manquants : {', '.join(missing_prereqs)}"
        
        # Vérifier les ressources
        can_afford, missing_resources = await self.can_afford_research(village_id, research_key)
        if not can_afford:
            return None, f"Ressources insuffisantes : {missing_resources}"
        
        # Consommer les ressources
        data = RESEARCH_TREE[research_key]
        costs = data.get("costs", {})
        success = await self.village_service.consume_resources(village_id, costs)
        if not success:
            return None, "Erreur lors de la consommation des ressources"
        
        # Démarrer la recherche
        duration_hours = data.get("duration_hours", 1)
        research.status = ResearchStatus.IN_PROGRESS
        research.progress = 0
        research.started_at = datetime.utcnow()
        research.completed_at = datetime.utcnow() + timedelta(hours=duration_hours)
        
        await self.db.commit()
        await self.db.refresh(research)
        
        return research, None
    
    async def complete_research(
        self,
        research_id: UUID,
        force: bool = False
    ) -> tuple[Optional[Research], Optional[str]]:
        """
        Complète une recherche.
        Si force=False, vérifie que la durée est écoulée.
        Si force=True, complète immédiatement (pour les workers ou admin).
        """
        research = await self.get_research(research_id)
        if not research:
            return None, "Recherche introuvable"
        
        if research.status != ResearchStatus.IN_PROGRESS:
            return None, "La recherche n'est pas en cours"
        
        # Vérifier la durée si non forcé
        if not force and research.completed_at:
            if datetime.utcnow() < research.completed_at:
                remaining = (research.completed_at - datetime.utcnow()).total_seconds() / 3600
                return None, f"Recherche pas encore terminée ({remaining:.1f}h restantes)"
        
        # Compléter la recherche
        research.status = ResearchStatus.COMPLETED
        research.progress = 100
        research.completed_at = datetime.utcnow()
        
        # Débloquer les recherches dépendantes
        await self._unlock_dependent_researches(research.village_id, research.research_key)
        
        await self.db.commit()
        await self.db.refresh(research)
        
        return research, None
    
    async def _unlock_dependent_researches(self, village_id: UUID, completed_key: str):
        """
        Débloque les recherches qui dépendaient de celle-ci.
        Vérifie tous les prérequis de chaque recherche LOCKED.
        """
        locked = await self.get_village_researches(
            village_id=village_id,
            status=ResearchStatus.LOCKED
        )
        
        for research in locked:
            can_unlock, _ = await self.check_prerequisites(village_id, research.research_key)
            if can_unlock:
                research.status = ResearchStatus.AVAILABLE
        
        await self.db.commit()
    
    async def cancel_research(self, research_id: UUID) -> tuple[Optional[Research], Optional[str]]:
        """
        Annule une recherche en cours.
        Ne rembourse PAS les ressources (coût de l'annulation).
        """
        research = await self.get_research(research_id)
        if not research:
            return None, "Recherche introuvable"
        
        if research.status != ResearchStatus.IN_PROGRESS:
            return None, "La recherche n'est pas en cours"
        
        # Retour à AVAILABLE
        research.status = ResearchStatus.AVAILABLE
        research.progress = 0
        research.started_at = None
        research.completed_at = None
        
        await self.db.commit()
        await self.db.refresh(research)
        
        return research, None
    
    async def get_tech_tree(self, village_id: UUID) -> Dict[str, Any]:
        """
        Récupère l'arbre technologique complet du village.
        Structure : {category: [researches avec détails + statut]}
        """
        researches = await self.get_village_researches(village_id)
        
        # Organiser par catégorie
        tree = {
            ResearchCategory.AGRICULTURE: [],
            ResearchCategory.MILITARY: [],
            ResearchCategory.ECONOMY: [],
            ResearchCategory.SCIENCE: []
        }
        
        for research in researches:
            details = await self.get_research_details(research.research_key)
            tree[research.category].append({
                "id": research.id,
                "research_key": research.research_key,
                "status": research.status,
                "progress": research.progress,
                "started_at": research.started_at,
                "completed_at": research.completed_at,
                **details
            })
        
        return tree
    
    async def get_research_bonuses(self, village_id: UUID) -> Dict[str, Any]:
        """
        Calcule tous les bonus actifs des recherches complétées.
        Retourne un dict avec tous les bonus cumulés.
        """
        completed = await self.get_village_researches(
            village_id=village_id,
            status=ResearchStatus.COMPLETED
        )
        
        bonuses = {
            "production_multiplier": 1.0,  # Multiplicateur de production
            "mission_success_bonus": 0,     # Bonus % taux de succès missions
            "construction_speed": 1.0,      # Vitesse de construction
            "research_speed": 1.0,          # Vitesse de recherche
            "unlocked_buildings": [],       # Bâtiments débloqués
            "unlocked_equipment": [],       # Équipements débloqués
            "special_abilities": []         # Capacités spéciales
        }
        
        for research in completed:
            data = RESEARCH_TREE.get(research.research_key, {})
            effects = data.get("effects", {})
            
            # Appliquer les effets
            if "production_bonus" in effects:
                bonuses["production_multiplier"] += effects["production_bonus"] / 100
            
            if "mission_success_bonus" in effects:
                bonuses["mission_success_bonus"] += effects["mission_success_bonus"]
            
            if "construction_speed_bonus" in effects:
                bonuses["construction_speed"] += effects["construction_speed_bonus"] / 100
            
            if "research_speed_bonus" in effects:
                bonuses["research_speed"] += effects["research_speed_bonus"] / 100
            
            if "unlocks_buildings" in effects:
                bonuses["unlocked_buildings"].extend(effects["unlocks_buildings"])
            
            if "unlocks_equipment" in effects:
                bonuses["unlocked_equipment"].extend(effects["unlocks_equipment"])
            
            if "special_ability" in effects:
                bonuses["special_abilities"].append(effects["special_ability"])
        
        return bonuses
