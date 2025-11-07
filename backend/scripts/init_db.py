"""
Script d'initialisation de la base de données.
Crée toutes les tables et insère les données de référence (bâtiments).
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le dossier racine au path pour les imports
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.database import engine, Base, AsyncSessionLocal
from backend.app.models import Building
from backend.app.utils.seed_data import BUILDINGS_DATA


async def create_tables():
    """Crée toutes les tables de la base de données"""
    print("🔨 Création des tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Tables créées avec succès!")


async def seed_buildings(session: AsyncSession):
    """Insère les données de référence des bâtiments"""
    print("🏗️  Insertion des bâtiments de référence...")
    
    # Vérifier si des bâtiments existent déjà
    result = await session.execute(select(Building))
    existing_buildings = result.scalars().all()
    
    if existing_buildings:
        print(f"⚠️  {len(existing_buildings)} bâtiments déjà présents, skip du seed.")
        return
    
    # Insérer les bâtiments
    for building_data in BUILDINGS_DATA:
        building = Building(**building_data)
        session.add(building)
    
    await session.commit()
    print(f"✅ {len(BUILDINGS_DATA)} bâtiments insérés avec succès!")


async def init_database():
    """Point d'entrée principal - initialise la base de données complète"""
    print("🚀 Initialisation de la base de données Loots&Live\n")
    
    try:
        # Créer les tables
        await create_tables()
        
        # Seed des données de référence
        async with AsyncSessionLocal() as session:
            await seed_buildings(session)
        
        print("\n🎉 Base de données initialisée avec succès!")
        print("📍 Fichier: data/lootsandlive.db")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'initialisation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(init_database())
