"""
Service métier pour la gestion des utilisateurs.
Gère les opérations CRUD et la logique métier liée aux comptes utilisateurs.
"""

from typing import Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.user import User
from backend.app.schemas.user import UserUpdate, UserResponse
from backend.app.utils.auth import get_password_hash


class UserService:
    """Service pour la gestion des utilisateurs"""
    
    def __init__(self, db: AsyncSession):
        """
        Initialise le service utilisateur
        
        Args:
            db: Session de base de données asynchrone
        """
        self.db = db
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Récupère un utilisateur par son ID
        
        Args:
            user_id: Identifiant de l'utilisateur
            
        Returns:
            User si trouvé, None sinon
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """
        Récupère un utilisateur par son nom d'utilisateur
        
        Args:
            username: Nom d'utilisateur
            
        Returns:
            User si trouvé, None sinon
        """
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Récupère un utilisateur par son email
        
        Args:
            email: Adresse email
            
        Returns:
            User si trouvé, None sinon
        """
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def update_user_profile(
        self, 
        user_id: int, 
        user_update: UserUpdate
    ) -> Optional[User]:
        """
        Met à jour le profil d'un utilisateur
        
        Args:
            user_id: Identifiant de l'utilisateur
            user_update: Données de mise à jour
            
        Returns:
            User mis à jour si trouvé, None sinon
            
        Raises:
            ValueError: Si le nouveau username/email est déjà utilisé
        """
        # Récupérer l'utilisateur
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Vérifier l'unicité du username si modification
        if user_update.username and user_update.username != user.username:
            existing = await self.get_user_by_username(user_update.username)
            if existing:
                raise ValueError(f"Le nom d'utilisateur '{user_update.username}' est déjà utilisé")
            user.username = user_update.username
        
        # Vérifier l'unicité de l'email si modification
        if user_update.email and user_update.email != user.email:
            existing = await self.get_user_by_email(user_update.email)
            if existing:
                raise ValueError(f"L'email '{user_update.email}' est déjà utilisé")
            user.email = user_update.email
        
        # Mettre à jour le mot de passe si fourni
        if user_update.password:
            user.hashed_password = get_password_hash(user_update.password)
        
        # Sauvegarder
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def update_last_login(self, user_id: int) -> None:
        """
        Met à jour la date de dernière connexion
        
        Args:
            user_id: Identifiant de l'utilisateur
        """
        user = await self.get_user_by_id(user_id)
        if user:
            user.last_login = datetime.utcnow()
            await self.db.commit()
    
    async def delete_user(self, user_id: int) -> bool:
        """
        Supprime un utilisateur
        
        Note: En production, on préfère désactiver plutôt que supprimer.
        Ici on supprime réellement pour respecter RGPD.
        
        Args:
            user_id: Identifiant de l'utilisateur
            
        Returns:
            True si supprimé, False si non trouvé
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return False
        
        await self.db.delete(user)
        await self.db.commit()
        
        return True
    
    async def deactivate_user(self, user_id: int) -> Optional[User]:
        """
        Désactive un utilisateur (soft delete)
        
        Args:
            user_id: Identifiant de l'utilisateur
            
        Returns:
            User désactivé si trouvé, None sinon
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        user.is_active = False
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def activate_user(self, user_id: int) -> Optional[User]:
        """
        Réactive un utilisateur
        
        Args:
            user_id: Identifiant de l'utilisateur
            
        Returns:
            User réactivé si trouvé, None sinon
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        user.is_active = True
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def get_user_stats(self, user_id: int) -> Optional[dict]:
        """
        Récupère les statistiques d'un utilisateur
        
        Args:
            user_id: Identifiant de l'utilisateur
            
        Returns:
            Dictionnaire avec les stats si trouvé, None sinon
        """
        user = await self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Récupérer le village du joueur (pour stats avancées)
        village = user.villages[0] if user.villages else None
        
        stats = {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "created_at": user.created_at,
            "last_login": user.last_login,
            "has_village": village is not None,
        }
        
        if village:
            stats["village_id"] = village.id
            stats["village_name"] = village.name
            stats["village_level"] = village.level
        
        return stats
