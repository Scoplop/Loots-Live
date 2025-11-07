"""
Service pour la gestion des missions d'exploration.
"""

from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from datetime import datetime, timedelta
import random

from backend.app.models.mission import Mission
from backend.app.models.mission_participant import MissionParticipant
from backend.app.models.village import Village
from backend.app.models.character import Character
from backend.app.models.resource import Resource
from backend.app.schemas.mission import (
    MissionCreate,
    MissionResponse,
    MissionComplete
)
from backend.app.utils.constants import MissionType, MissionStatus


class MissionService:
    """Service pour gérer les missions"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_mission(
        self,
        user_id: int,
        mission_data: MissionCreate
    ) -> Mission:
        """
        Crée une nouvelle mission (préparation).
        La mission n'est pas encore lancée, les PNJ sont assignés.
        """
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

        # Vérifier le nombre de participants (2-5)
        if len(mission_data.participant_ids) < 2 or len(mission_data.participant_ids) > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Une mission nécessite entre 2 et 5 participants"
            )

        # Vérifier que tous les participants existent et appartiennent au village
        participants = []
        for character_id in mission_data.participant_ids:
            char_result = await self.db.execute(
                select(Character).where(
                    Character.id == character_id,
                    Character.village_id == village.id
                )
            )
            character = char_result.scalar_one_or_none()
            
            if not character:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Personnage {character_id} non trouvé dans le village"
                )
            
            if character.is_on_mission:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{character.name} est déjà en mission"
                )
            
            if character.current_hp <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"{character.name} est incapacité (0 HP)"
                )
            
            participants.append(character)

        # Créer la mission
        new_mission = Mission(
            village_id=village.id,
            name=mission_data.name,
            description=mission_data.description,
            mission_type=mission_data.mission_type.value,
            status=MissionStatus.PREPARING.value,
            difficulty=mission_data.difficulty,
            duration_minutes=mission_data.duration_minutes,
            rewards=mission_data.rewards
        )

        self.db.add(new_mission)
        await self.db.commit()
        await self.db.refresh(new_mission)

        # Ajouter les participants
        for character in participants:
            participant = MissionParticipant(
                mission_id=new_mission.id,
                character_id=character.id
            )
            self.db.add(participant)

        await self.db.commit()
        await self.db.refresh(new_mission)

        return new_mission

    async def start_mission(
        self,
        mission_id: int,
        user_id: int
    ) -> Mission:
        """
        Lance une mission (passe de PREPARING à IN_PROGRESS).
        Marque les PNJ comme en mission.
        """
        # Récupérer la mission
        mission = await self.get_mission_by_id(mission_id, user_id)
        if not mission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mission non trouvée"
            )

        if mission.status != MissionStatus.PREPARING.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La mission n'est pas en préparation"
            )

        # Marquer les participants comme en mission
        for participant in mission.participants:
            character_result = await self.db.execute(
                select(Character).where(Character.id == participant.character_id)
            )
            character = character_result.scalar_one_or_none()
            if character:
                character.is_on_mission = True

        # Démarrer la mission
        mission.status = MissionStatus.IN_PROGRESS.value
        mission.started_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(mission)

        return mission

    async def complete_mission(
        self,
        mission_id: int,
        user_id: int
    ) -> MissionComplete:
        """
        Termine une mission et calcule les résultats.
        Distribue récompenses, XP, gère les blessures.
        """
        # Récupérer la mission
        mission = await self.get_mission_by_id(mission_id, user_id)
        if not mission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mission non trouvée"
            )

        if mission.status != MissionStatus.IN_PROGRESS.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La mission n'est pas en cours"
            )

        # Vérifier que la durée est écoulée (en production, géré par workers)
        # Pour l'instant, on permet de terminer immédiatement
        # if mission.started_at:
        #     elapsed = (datetime.utcnow() - mission.started_at).total_seconds() / 60
        #     if elapsed < mission.duration_minutes:
        #         raise HTTPException(...)

        # Calculer le taux de réussite
        success_rate = await self.calculate_success_rate(mission_id)
        
        # Lancer le dé
        success = random.random() < success_rate

        # Récupérer les participants
        participants = []
        for participant in mission.participants:
            char_result = await self.db.execute(
                select(Character).where(Character.id == participant.character_id)
            )
            character = char_result.scalar_one_or_none()
            if character:
                participants.append(character)

        # Calculer récompenses et casualties
        rewards_obtained = {}
        casualties = []
        xp_gained = 0

        if success:
            # Mission réussie
            mission.status = MissionStatus.COMPLETED.value
            
            # Distribuer récompenses complètes
            if "resources" in mission.rewards:
                rewards_obtained = mission.rewards["resources"]
                await self._add_resources_to_village(mission.village_id, rewards_obtained)
            
            # XP pour tous les participants
            base_xp = mission.rewards.get("xp", 100)
            xp_gained = base_xp
            
            for character in participants:
                await self._grant_xp(character.id, xp_gained)
                character.is_on_mission = False
            
            # Chance d'équipement (TODO: quand Equipment service sera créé)
            # equipment_chance = mission.rewards.get("equipment_chance", 0)
            
        else:
            # Mission échouée
            mission.status = MissionStatus.FAILED.value
            
            # Récompenses partielles (30%)
            if "resources" in mission.rewards:
                partial_rewards = {
                    res: int(qty * 0.3) 
                    for res, qty in mission.rewards["resources"].items()
                }
                rewards_obtained = partial_rewards
                await self._add_resources_to_village(mission.village_id, partial_rewards)
            
            # XP réduite
            base_xp = mission.rewards.get("xp", 100)
            xp_gained = int(base_xp * 0.3)
            
            # Casualties (30% de chance de blessure par participant)
            for character in participants:
                await self._grant_xp(character.id, xp_gained)
                character.is_on_mission = False
                
                if random.random() < 0.3:
                    # Blessure : perte de 30-50% HP
                    damage_percent = random.uniform(0.3, 0.5)
                    damage = int(character.max_hp * damage_percent)
                    character.current_hp = max(0, character.current_hp - damage)
                    casualties.append(character.id)

        # Terminer la mission
        mission.completed_at = datetime.utcnow()

        await self.db.commit()

        return MissionComplete(
            mission_id=mission.id,
            success=success,
            rewards_obtained=rewards_obtained,
            casualties=casualties,
            xp_gained=xp_gained
        )

    async def recall_mission(
        self,
        mission_id: int,
        user_id: int
    ) -> Mission:
        """
        Rappelle une mission en cours (annulation).
        Aucune récompense, mais PNJ rentrent sans dégâts.
        """
        # Récupérer la mission
        mission = await self.get_mission_by_id(mission_id, user_id)
        if not mission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mission non trouvée"
            )

        if mission.status != MissionStatus.IN_PROGRESS.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Seules les missions en cours peuvent être rappelées"
            )

        # Libérer les participants
        for participant in mission.participants:
            char_result = await self.db.execute(
                select(Character).where(Character.id == participant.character_id)
            )
            character = char_result.scalar_one_or_none()
            if character:
                character.is_on_mission = False

        # Marquer comme rappelée
        mission.status = MissionStatus.RECALLED.value
        mission.completed_at = datetime.utcnow()

        await self.db.commit()
        await self.db.refresh(mission)

        return mission

    async def calculate_success_rate(self, mission_id: int) -> float:
        """
        Calcule le taux de réussite d'une mission.
        
        Formule:
        - Score équipe = Σ(puissance_PNJ) / nb_participants
        - Taux base = min(0.9, Score équipe / (difficulté × 50))
        - Bonus chef: +5% si un Leader dans l'équipe
        - Malus moral: -10% si moral village < 50
        """
        # Récupérer la mission
        result = await self.db.execute(
            select(Mission).where(Mission.id == mission_id)
        )
        mission = result.scalar_one_or_none()
        if not mission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mission non trouvée"
            )

        # Récupérer les participants
        participants = []
        has_leader = False
        total_power = 0

        for participant in mission.participants:
            char_result = await self.db.execute(
                select(Character).where(Character.id == participant.character_id)
            )
            character = char_result.scalar_one_or_none()
            if character:
                participants.append(character)
                
                # Calculer puissance du PNJ
                power = (
                    character.strength +
                    character.dexterity +
                    character.endurance +
                    character.intelligence +
                    character.speed +
                    character.luck
                )
                total_power += power
                
                # Vérifier si Leader
                if character.character_class == "leader":
                    has_leader = True

        if not participants:
            return 0.0

        # Score moyen de l'équipe
        team_score = total_power / len(participants)

        # Taux de base (difficulté × 50 = puissance requise)
        required_power = mission.difficulty * 50
        base_rate = min(0.9, team_score / required_power)

        # Bonus chef
        leader_bonus = 0.05 if has_leader else 0.0

        # Bonus/malus moral (TODO: récupérer moral du village)
        # village_result = await self.db.execute(...)
        # moral_bonus = -0.1 if village.moral < 50 else 0.0
        moral_bonus = 0.0  # Placeholder

        # Taux final (entre 0.1 et 0.95)
        final_rate = max(0.1, min(0.95, base_rate + leader_bonus + moral_bonus))

        return final_rate

    async def get_mission_by_id(
        self,
        mission_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Mission]:
        """Récupère une mission par ID (avec vérification propriétaire optionnelle)"""
        query = select(Mission).where(Mission.id == mission_id)
        
        if user_id:
            # Vérifier que la mission appartient au village de l'utilisateur
            village_result = await self.db.execute(
                select(Village).where(Village.user_id == user_id)
            )
            village = village_result.scalar_one_or_none()
            if not village:
                return None
            
            query = query.where(Mission.village_id == village.id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_village_missions(
        self,
        user_id: int,
        status_filter: Optional[MissionStatus] = None
    ) -> List[Mission]:
        """Récupère toutes les missions du village (filtre optionnel par statut)"""
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

        # Récupérer les missions
        query = select(Mission).where(Mission.village_id == village.id)
        
        if status_filter:
            query = query.where(Mission.status == status_filter.value)
        
        query = query.order_by(Mission.created_at.desc())

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def delete_mission(
        self,
        mission_id: int,
        user_id: int
    ) -> bool:
        """
        Supprime une mission (uniquement si PREPARING ou terminée).
        Impossible de supprimer une mission en cours.
        """
        mission = await self.get_mission_by_id(mission_id, user_id)
        if not mission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Mission non trouvée"
            )

        if mission.status == MissionStatus.IN_PROGRESS.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de supprimer une mission en cours. Utilisez /recall."
            )

        await self.db.delete(mission)
        await self.db.commit()

        return True

    async def generate_random_mission(
        self,
        user_id: int,
        mission_type: MissionType
    ) -> Dict[str, Any]:
        """
        Génère une mission aléatoire (proposition).
        Retourne les paramètres sans créer la mission.
        """
        # Récupérer le village pour ajuster difficulté
        village_result = await self.db.execute(
            select(Village).where(Village.user_id == user_id)
        )
        village = village_result.scalar_one_or_none()
        if not village:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Village non trouvé"
            )

        # Difficulté aléatoire (1-10)
        difficulty = random.randint(1, 10)

        # Durée selon type
        duration_ranges = {
            MissionType.HARVEST: (30, 120),
            MissionType.RESCUE: (60, 240),
            MissionType.EXPLORATION: (120, 480)
        }
        min_dur, max_dur = duration_ranges.get(mission_type, (60, 180))
        duration = random.randint(min_dur, max_dur)

        # Récompenses selon type et difficulté
        base_resources = {
            MissionType.HARVEST: ["water", "wood", "stone", "food"],
            MissionType.RESCUE: ["herb", "food", "cloth"],
            MissionType.EXPLORATION: ["metal", "rare_ore", "ancient_relic", "gem"]
        }

        # Sélectionner 1-3 ressources
        available_resources = base_resources.get(mission_type, ["food"])
        num_resources = random.randint(1, 3)
        selected_resources = random.sample(available_resources, min(num_resources, len(available_resources)))

        # Quantités selon difficulté
        rewards = {
            "resources": {
                res: random.randint(10 * difficulty, 30 * difficulty)
                for res in selected_resources
            },
            "xp": 50 * difficulty,
            "equipment_chance": min(0.3, 0.05 * difficulty)
        }

        # Noms et descriptions
        mission_names = {
            MissionType.HARVEST: [
                "Récolte aux abords du village",
                "Collecte de ressources",
                "Expédition de ravitaillement"
            ],
            MissionType.RESCUE: [
                "Sauvetage d'un groupe égaré",
                "Mission de secours",
                "Recherche de survivants"
            ],
            MissionType.EXPLORATION: [
                "Exploration des ruines",
                "Reconnaissance du territoire",
                "Expédition vers l'inconnu"
            ]
        }

        name = random.choice(mission_names.get(mission_type, ["Mission"]))
        description = f"Une mission de type {mission_type.value} de difficulté {difficulty}/10. Durée estimée: {duration} minutes."

        return {
            "name": name,
            "description": description,
            "mission_type": mission_type.value,
            "difficulty": difficulty,
            "duration_minutes": duration,
            "rewards": rewards
        }

    # ============================================================================
    # MÉTHODES PRIVÉES
    # ============================================================================

    async def _add_resources_to_village(
        self,
        village_id: int,
        resources: Dict[str, int]
    ):
        """Ajoute des ressources au village"""
        # Récupérer ressources existantes
        result = await self.db.execute(
            select(Resource).where(Resource.village_id == village_id)
        )
        existing_resources = {r.resource_type: r for r in result.scalars().all()}

        # Ajouter
        for resource_type, amount in resources.items():
            if resource_type in existing_resources:
                existing_resources[resource_type].quantity += amount
            else:
                # Créer la ressource si elle n'existe pas
                new_resource = Resource(
                    village_id=village_id,
                    resource_type=resource_type,
                    quantity=amount
                )
                self.db.add(new_resource)

        await self.db.commit()

    async def _grant_xp(self, character_id: int, xp_amount: int):
        """Donne de l'XP à un personnage"""
        from backend.app.services.character_service import CharacterService
        
        char_service = CharacterService(self.db)
        await char_service.gain_xp(character_id, xp_amount)
