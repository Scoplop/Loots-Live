"""
Service d'authentification - Inscription et connexion.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from backend.app.models.user import User
from backend.app.schemas.user import UserCreate, UserLogin, Token
from backend.app.utils.auth import get_password_hash, verify_password, create_access_token


class AuthService:
    """Service pour gérer l'authentification des utilisateurs"""
    
    @staticmethod
    async def register_user(db: AsyncSession, user_data: UserCreate) -> User:
        """
        Inscrit un nouvel utilisateur.
        
        Args:
            db: Session de base de données
            user_data: Données d'inscription
        
        Returns:
            User: Utilisateur créé
        
        Raises:
            HTTPException: Si le username ou email existe déjà
        """
        # Vérifier si le username existe déjà
        result = await db.execute(select(User).where(User.username == user_data.username))
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ce nom d'utilisateur existe déjà"
            )
        
        # Vérifier si l'email existe déjà (si fourni)
        if user_data.email:
            result = await db.execute(select(User).where(User.email == user_data.email))
            existing_email = result.scalar_one_or_none()
            
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cet email est déjà utilisé"
                )
        
        # Hasher le mot de passe
        hashed_password = get_password_hash(user_data.password)
        
        # Créer l'utilisateur
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            created_at=datetime.utcnow(),
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        return new_user
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, login_data: UserLogin) -> Optional[User]:
        """
        Authentifie un utilisateur.
        
        Args:
            db: Session de base de données
            login_data: Données de connexion
        
        Returns:
            User si authentification réussie, None sinon
        """
        # Récupérer l'utilisateur par username
        result = await db.execute(select(User).where(User.username == login_data.username))
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Vérifier le mot de passe
        if not verify_password(login_data.password, user.password_hash):
            return None
        
        # Mettre à jour la date de dernière connexion
        user.last_login = datetime.utcnow()
        await db.commit()
        
        return user
    
    @staticmethod
    def create_user_token(user: User) -> Token:
        """
        Crée un token JWT pour un utilisateur.
        
        Args:
            user: Utilisateur
        
        Returns:
            Token: Token d'accès
        """
        access_token = create_access_token(
            data={"user_id": user.id, "username": user.username}
        )
        
        return Token(access_token=access_token, token_type="bearer")
    
    @staticmethod
    async def login(db: AsyncSession, login_data: UserLogin) -> Token:
        """
        Connexion complète : authentification + génération de token.
        
        Args:
            db: Session de base de données
            login_data: Données de connexion
        
        Returns:
            Token: Token d'accès
        
        Raises:
            HTTPException: Si l'authentification échoue
        """
        user = await AuthService.authenticate_user(db, login_data)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nom d'utilisateur ou mot de passe incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return AuthService.create_user_token(user)
