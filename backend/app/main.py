"""
Application principale FastAPI - Loots&Live.
Point d'entrée du serveur backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.app.config import settings
from backend.app.database import init_db, close_db
from backend.app.routes import auth, user, village, character, building, mission, equipment, research, worker
from backend.app.workers.worker_manager import worker_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestion du cycle de vie de l'application.
    Initialise et ferme les ressources (base de données, workers, etc.).
    """
    # Startup: Initialiser la base de données
    print("🚀 Démarrage de Loots&Live...")
    await init_db()
    print("✅ Base de données initialisée")
    
    # Startup: Démarrer les workers background
    worker_manager.start()
    print("✅ Workers background démarrés")
    
    yield
    
    # Shutdown: Arrêter les workers
    print("🛑 Arrêt de Loots&Live...")
    worker_manager.stop()
    print("✅ Workers arrêtés")
    
    # Shutdown: Fermer les connexions
    await close_db()
    print("✅ Connexions fermées")


# Création de l'application FastAPI
app = FastAPI(
    title="Loots&Live API",
    description="""
    API backend pour Loots&Live - Jeu de gestion post-apocalyptique.
    
    ## Fonctionnalités
    
    * **Authentification**: Inscription, connexion JWT
    * **Villages**: Gestion de votre village
    * **Personnages**: PNJ joueur et IA avec stats, équipement, apparence
    * **Bâtiments**: Construction et production de ressources
    * **Missions**: Exploration avec équipes de PNJ
    * **Relations**: Système de relations entre PNJ (-100 à +100)
    * **Recherches**: Arbre technologique
    * **Chat IA**: Conversations contextuelles avec Ollama
    * **Événements**: Événements aléatoires procéduraux
    
    ## Technologies
    
    * FastAPI + SQLAlchemy async
    * SQLite
    * Ollama (IA locale)
    * JWT Authentication
    """,
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configuration CORS (pour permettre les requêtes depuis le frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Inclusion des routes
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(village.router)
app.include_router(character.router)
app.include_router(building.router)
app.include_router(mission.router)
app.include_router(equipment.router)
app.include_router(research.router)
app.include_router(worker.router)


@app.get("/", tags=["Root"])
async def root():
    """
    Route racine - Informations sur l'API.
    """
    return {
        "message": "Bienvenue sur l'API Loots&Live",
        "version": "0.1.0",
        "docs": "/docs",
        "status": "online"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Vérification de santé du serveur.
    """
    return {
        "status": "healthy",
        "database": "connected",
        "ollama": "not_configured"  # TODO: vérifier Ollama
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
