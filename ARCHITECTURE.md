# Architecture Technique - Loots&Live

## Vue d'ensemble

**Loots&Live** est une application web de jeu de gestion post-apocalyptique avec IA générative pour les dialogues PNJ.

### Stack technologique retenue

#### Backend
- **Framework Web**: **FastAPI** ✓ (choisi pour ses performances, documentation automatique, async natif, et websockets intégrés)
- **ORM**: SQLAlchemy 2.0+ (avec support async)
- **Base de données**: SQLite (simple, portable, suffisant pour usage local mono-utilisateur)
- **Authentification**: JWT (avec bcrypt pour hash des mots de passe)
- **IA**: Client Ollama (http://localhost:11434/api/generate)
- **Background Tasks**: APScheduler (pour les timers et automatisations)

#### Frontend
- **Framework**: HTML5 + CSS3 + JavaScript Vanilla (+ libs légères)
- **Rendu graphique**: Canvas 2D (plus simple que WebGL, suffisant pour le style visuel voulu)
- **Communication API**: Fetch API (natif) + EventSource/WebSocket pour temps réel
- **State Management**: Simple object store en mémoire
- **UI Components**: Custom (pas de framework lourd, optimisation mobile first)

### Justification des choix

**Pourquoi FastAPI plutôt que Flask ?**
- Documentation automatique (Swagger/OpenAPI) intégrée
- Support natif async/await (important pour IA Ollama, websockets, background tasks)
- Validation automatique des données (Pydantic models)
- Performance supérieure (basé sur Starlette/Uvicorn)
- Meilleure structure pour un projet complexe

**Pourquoi pas de framework JS (React/Vue) ?**
- Mobile-first: bundle size critique
- Projet local mono-utilisateur: pas besoin de complexité SPA
- Canvas rendering: meilleure performance avec vanilla JS
- Contrôle total sur optimisations

**Pourquoi SQLite ?**
- Zéro configuration
- Fichier unique portable
- Performances largement suffisantes pour usage local
- Backup/export simple (copie de fichier)
- Pas de serveur à gérer

## Structure du projet

```
LootsAndLive/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # Point d'entrée FastAPI
│   │   ├── config.py               # Configuration (env variables, constantes)
│   │   ├── database.py             # Connexion DB, session management
│   │   ├── models/                 # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── character.py
│   │   │   ├── building.py
│   │   │   ├── resource.py
│   │   │   ├── mission.py
│   │   │   ├── equipment.py
│   │   │   ├── research.py
│   │   │   ├── relationship.py
│   │   │   ├── event.py
│   │   │   └── village_ai.py
│   │   ├── schemas/                # Pydantic schemas (validation, serialization)
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── character.py
│   │   │   └── ...
│   │   ├── routes/                 # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   ├── village.py
│   │   │   ├── buildings.py
│   │   │   ├── characters.py
│   │   │   ├── missions.py
│   │   │   ├── research.py
│   │   │   ├── equipment.py
│   │   │   ├── chat.py
│   │   │   └── progression.py
│   │   ├── services/               # Logique métier
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── character_service.py
│   │   │   ├── building_service.py
│   │   │   ├── mission_service.py
│   │   │   ├── combat_service.py
│   │   │   ├── equipment_service.py
│   │   │   ├── ai_service.py       # Ollama integration
│   │   │   ├── event_service.py    # Événements procéduraux
│   │   │   └── automation_service.py
│   │   ├── utils/                  # Utilitaires
│   │   │   ├── __init__.py
│   │   │   ├── security.py         # JWT, bcrypt
│   │   │   ├── constants.py        # Constantes du jeu
│   │   │   ├── formulas.py         # Formules (XP, combat, etc.)
│   │   │   ├── generators.py       # Génération procédurale
│   │   │   └── validators.py
│   │   └── workers/                # Background tasks
│   │       ├── __init__.py
│   │       ├── mission_worker.py   # Check missions toutes les 5s
│   │       ├── production_worker.py # Production bâtiments
│   │       ├── healing_worker.py   # Guérison PNJ
│   │       └── event_worker.py     # Événements village (6h)
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   ├── test_routes.py
│   │   ├── test_services.py
│   │   ├── test_formulas.py
│   │   └── test_integration.py
│   └── scripts/
│       ├── init_db.py              # Création tables + données de base
│       ├── export_db.py            # Backup SQLite
│       ├── reset_accounts.py       # Suppression comptes
│       └── seed_data.py            # Données de test
├── frontend/
│   ├── index.html                  # Page d'accueil
│   ├── css/
│   │   ├── main.css                # Styles globaux
│   │   ├── theme.css               # Thème post-apocalyptique
│   │   ├── village.css
│   │   ├── buildings.css
│   │   ├── characters.css
│   │   └── responsive.css
│   ├── js/
│   │   ├── app.js                  # Point d'entrée
│   │   ├── api/                    # Clients API
│   │   │   ├── auth.js
│   │   │   ├── village.js
│   │   │   ├── buildings.js
│   │   │   ├── characters.js
│   │   │   ├── missions.js
│   │   │   └── chat.js
│   │   ├── components/             # Composants UI
│   │   │   ├── navbar.js
│   │   │   ├── modal.js
│   │   │   ├── card.js
│   │   │   └── ...
│   │   ├── pages/                  # Pages (SPA-like)
│   │   │   ├── login.js
│   │   │   ├── character_creation.js
│   │   │   ├── village.js
│   │   │   ├── buildings.js
│   │   │   ├── characters.js
│   │   │   ├── missions.js
│   │   │   ├── research.js
│   │   │   └── progression.js
│   │   ├── renderers/              # Rendu Canvas
│   │   │   ├── village_renderer.js # Isométrique
│   │   │   ├── character_renderer.js
│   │   │   ├── building_renderer.js
│   │   │   └── ai_village_renderer.js
│   │   ├── utils/
│   │   │   ├── state.js            # State management simple
│   │   │   ├── router.js           # Client-side routing
│   │   │   ├── helpers.js
│   │   │   └── constants.js
│   │   └── workers/
│   │       └── background.js       # Web Workers si besoin
│   └── assets/
│       ├── sprites/                # Sprites PNJ, bâtiments
│       ├── icons/                  # Icônes UI
│       ├── sounds/                 # Sons (optionnel)
│       └── fonts/
├── data/
│   ├── lootsandlive.db             # Base SQLite (généré)
│   └── backups/                    # Backups DB
├── logs/
│   ├── app.log                     # Logs application
│   └── errors.log
├── scripts/                        # Scripts Windows
│   ├── start_server.bat
│   ├── stop_server.bat
│   ├── restart_server.bat
│   ├── install_dependencies.bat
│   └── update_app.bat
├── .env                            # Variables d'environnement
├── .gitignore
├── requirements.txt                # Dépendances Python
├── README.md
├── ARCHITECTURE.md                 # Ce fichier
├── DATABASE.md                     # Documentation DB
├── GUIDE_JOUEUR.md
└── Descritpion.txt                 # Spécifications (PO)
```

## Patterns et conventions

### Backend (FastAPI)

#### Architecture en couches (Layered Architecture)

```
Routes (API) → Services (Business Logic) → Models (Data Access) → Database
```

- **Routes**: Endpoints REST, validation entrée (Pydantic), retour JSON
- **Services**: Logique métier pure, calculs, orchestration
- **Models**: SQLAlchemy, accès DB, relations
- **Utils**: Fonctions pures réutilisables

#### Conventions de code

- **Nommage**:
  - Fichiers: `snake_case.py`
  - Classes: `PascalCase`
  - Fonctions/variables: `snake_case`
  - Constantes: `UPPER_SNAKE_CASE`

- **Type hints**: Obligatoires partout (Python 3.10+)
- **Docstrings**: Google style pour toutes les fonctions publiques
- **Async/Await**: Pour routes et services avec I/O (DB, Ollama)

#### Gestion des erreurs

- Exceptions custom héritées de `HTTPException`
- Codes HTTP standard (200, 201, 400, 401, 404, 500)
- Messages d'erreur clairs et localisés

### Frontend (Vanilla JS)

#### Architecture modulaire

```
Page → Components → Renderers → API
```

- **Pages**: Orchestration, state management local
- **Components**: UI réutilisables (modals, cards, forms)
- **Renderers**: Logique Canvas, sprites, animations
- **API**: Clients HTTP, WebSocket

#### Conventions de code

- **Nommage**:
  - Fichiers: `snake_case.js`
  - Classes: `PascalCase`
  - Fonctions: `camelCase`
  - Constantes: `UPPER_SNAKE_CASE`

- **Modules**: ES6 modules (`import`/`export`)
- **Async/Await**: Pour appels API
- **JSDoc**: Documentation des fonctions complexes

#### State Management

Objet global simple:
```javascript
const AppState = {
  user: null,
  village: null,
  characters: [],
  buildings: [],
  missions: [],
  // ...
};
```

Mise à jour via fonctions dédiées + événements custom pour notifier les composants.

## Sécurité

### Backend

- **Authentification**: JWT avec expiration 24h
- **Hash mots de passe**: bcrypt (cost factor 12)
- **Rate limiting**: 5 tentatives/10min par IP (login)
- **Validation**: Pydantic models pour toutes les entrées
- **SQL Injection**: Prévenu par SQLAlchemy ORM
- **CORS**: Configuré pour `http://localhost:*` uniquement

### Frontend

- **XSS**: Escape toutes les données utilisateur
- **CSRF**: Non nécessaire (JWT dans headers, pas de cookies)
- **localStorage**: Token JWT stocké (avec expiration)

## Performance

### Backend

- **Indexation DB**: Sur colonnes fréquemment requêtées (user_id, village_id, etc.)
- **Eager loading**: Relations SQLAlchemy (éviter N+1 queries)
- **Cache**: Redis optionnel pour données fréquentes (ressources, stats)
- **Pagination**: Listes longues (missions, événements)
- **Background tasks**: APScheduler pour timers (non-blocking)

### Frontend

- **Lazy loading**: Chargement progressif des pages
- **Canvas optimisations**:
  - Dirty rectangles (redessiner zones modifiées uniquement)
  - Off-screen canvas pour sprites
  - RequestAnimationFrame pour animations
- **Sprites**: Atlas de textures (1 image, multiple sprites)
- **Debounce/Throttle**: Événements fréquents (scroll, resize, search)
- **Web Workers**: Calculs lourds (génération procédurale)

## Base de données

### SQLite

- **Fichier**: `data/lootsandlive.db`
- **Migrations**: Alembic (non implémenté initialement, ajout manuel si besoin)
- **Backup**: Script `export_db.py` (copie fichier + export SQL)
- **Transactions**: Automatiques avec SQLAlchemy sessions

### Tables principales (résumé)

- `users`: Comptes joueurs
- `characters`: PNJ (joueur + IA)
- `buildings`: Bâtiments du village
- `resources`: Stocks de ressources
- `missions`: Missions en cours/terminées
- `equipment`: Équipements
- `researches`: Recherches débloquées
- `relationships`: Relations PNJ-PNJ
- `events`: Événements village
- `villages_ai`: Villages IA
- `conversations`: Historique chat

Voir `DATABASE.md` pour schéma complet.

## Intégration IA (Ollama)

### Configuration

- **Endpoint**: `http://localhost:11434/api/generate`
- **Modèle recommandé**: `llama3.1:8b` (équilibre perf/qualité)
- **Fallback**: Réponses prédéfinies si Ollama indisponible
- **Timeout**: 30 secondes
- **Queue**: Max 3 requêtes simultanées (éviter surcharge)

### Système de prompts

Structure modulaire:
```python
PROMPT_BASE = """Tu es {name}, un PNJ dans un village post-apocalyptique.
Personnalité: {personality}
Traits: {traits}
Moral: {mood}
Contexte: {context}

Conversation précédente:
{history}

Joueur: {user_message}
{name}:"""
```

Variables injectées dynamiquement selon contexte.

### Cache

- **Prompts personnalités**: Générés à la création du PNJ (stockés en DB)
- **Réponses fréquentes**: Cache Redis (optionnel)
- **Batch generation**: Dialogues PNJ-PNJ générés par lots (toutes les 6h)

## Tests

### Backend

- **Framework**: pytest + pytest-asyncio
- **Coverage**: Minimum 70% (objectif 85%)
- **Types**:
  - Unitaires: Modèles, services, formules
  - Intégration: Routes API avec DB en mémoire
  - E2E: Scénarios complets (création compte → prestige)

### Frontend

- **Framework**: Jest (optionnel, si temps)
- **Tests manuels**: Checklist complète avant release

## Déploiement local

### Prérequis

- Python 3.10+
- Ollama installé et en cours d'exécution
- Navigateur moderne (Chrome/Firefox/Edge)

### Installation

```bash
# 1. Créer venv
python -m venv venv
venv\Scripts\activate

# 2. Installer dépendances
pip install -r requirements.txt

# 3. Initialiser DB
python backend/scripts/init_db.py

# 4. Lancer serveur
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Ou utiliser `scripts/start_server.bat`

### Accès

- **Frontend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Évolutions futures possibles

- **Multi-joueur**: WebSocket pour villages partagés (nécessite refonte architecture)
- **Mobile app**: Wrapper Capacitor/Cordova
- **Modding**: API pour plugins personnalisés
- **Cloud save**: Sync DB avec service distant
- **Traductions**: i18n pour support multi-langues

---

**Dernière mise à jour**: 2025-11-07
**Version architecture**: 1.0
**Responsable**: GitHub Copilot (Développeur)
