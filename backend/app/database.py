"""
Configuration de la base de données SQLAlchemy.
Gère la connexion async à SQLite et les sessions.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

from backend.app.config import settings


# Base class pour tous les modèles
class Base(DeclarativeBase):
    """Classe de base pour tous les modèles SQLAlchemy"""
    pass


# Engine async SQLite
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries si DEBUG=True
    future=True,
    pool_pre_ping=True,  # Vérifier la connexion avant utilisation
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency FastAPI pour obtenir une session de base de données.
    
    Usage:
        @app.get("/...")
        async def endpoint(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialise la base de données (crée toutes les tables).
    À appeler au démarrage de l'application.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """
    Ferme la connexion à la base de données.
    À appeler à l'arrêt de l'application.
    """
    await engine.dispose()
