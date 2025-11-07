# 🏚️ Loots&Live - Jeu de Gestion Post-Apocalyptique

**Loots&Live** est une application web de jeu de gestion dans un univers post-apocalyptique inspiré de Fallout. Construisez votre village, gérez vos PNJ avec IA générative, partez en missions, et survivez dans le Wasteland !

## 🎮 Caractéristiques principales

- 🏘️ **Gestion de village**: Construction de 24 types de bâtiments (Maisons, Forges, Fermes, etc.)
- 👥 **PNJ intelligents**: Personnalités uniques, dialogues générés par IA (Ollama), relations complexes
- ⚔️ **Système de missions**: 3 types (Récolte, Sauvetage, Exploration) avec 100 niveaux de difficulté
- 🎯 **Combat tactique**: Tour par tour avec formules RPG (Force, Dextérité, Endurance, etc.)
- 🔬 **Arbre de recherche**: 40+ technologies en 7 branches
- ⚙️ **Équipement**: 6 raretés (Commun → Mythique), craft, génération procédurale
- 🌍 **Villages IA**: Diplomatie, commerce, guerres avec 4 villages IA
- 🏆 **Progression**: 100 niveaux + 10 cycles Prestige
- 🎨 **Interface**: Mobile-first, thème post-apocalyptique, vue isométrique

## 📋 Prérequis

- **Python 3.10+** (télécharger sur [python.org](https://www.python.org/downloads/))
- **Ollama** (IA pour dialogues PNJ) - [ollama.ai](https://ollama.ai/)
- **Navigateur moderne** (Chrome, Firefox, Edge)

### Installation d'Ollama

```bash
# Windows : Télécharger et installer depuis ollama.ai
# Puis télécharger un modèle (au choix) :

# Modèle recommandé (équilibré) :
ollama pull qwen2.5:14b

# Ou modèle léger (rapide) :
ollama pull llama3.2:latest

# Ou modèle premium (meilleur mais lourd) :
ollama pull qwen2.5:32b
```

**Modèles disponibles dans votre environnement** : qwen2.5:14b, qwen2.5:32b, llama3.2

## 🚀 Installation rapide

### Méthode 1 : Scripts Windows automatiques

```bash
# 1. Cloner ou télécharger le projet
cd LootsAndLive

# 2. Double-cliquer sur scripts\install_dependencies.bat
# Cela va créer l'environnement virtuel et installer les dépendances

# 3. Copier .env.example vers .env et éditer si besoin
copy .env.example .env

# 4. Initialiser la base de données
scripts\init_db.bat

# 5. Démarrer le serveur
scripts\start_server.bat
```

### Méthode 2 : Installation manuelle

```bash
# 1. Créer l'environnement virtuel
python -m venv venv
venv\Scripts\activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer l'application
copy .env.example .env
# Éditer .env si besoin (par défaut, ça fonctionne)

# 4. Initialiser la base de données
python backend\scripts\init_db.py

# 5. Lancer le serveur
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

## 🎯 Utilisation

1. **Ouvrez votre navigateur** : http://127.0.0.1:8000
2. **Créez un compte** : Pseudo + Mot de passe
3. **Créez votre personnage** : Apparence + Classe + Stats
4. **Jouez !** : Construisez, recrutez, explorez

## 🛠️ Scripts utiles

- `scripts\start_server.bat` : Démarre le serveur
- `scripts\stop_server.bat` : Arrête le serveur
- `scripts\restart_server.bat` : Redémarre le serveur
- `scripts\init_db.bat` : (Ré)initialise la base de données

## 📚 Documentation

- **[ARCHITECTURE.md](ARCHITECTURE.md)** : Architecture technique complète
- **[DATABASE.md](DATABASE.md)** : Schéma de base de données (à venir)
- **[GUIDE_JOUEUR.md](GUIDE_JOUEUR.md)** : Guide du joueur (à venir)
- **[Description.txt](Descritpion.txt)** : Spécifications détaillées (PO)

## 🔧 Configuration avancée

### Fichier .env

Principales variables :

```env
# Base de données
DATABASE_URL=sqlite+aiosqlite:///./data/lootsandlive.db

# Sécurité
SECRET_KEY=CHANGE_ME  # Important en production !

# Ollama
OLLAMA_ENDPOINT=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3.1:8b
```

### Modèles IA alternatifs

Vous disposez déjà de plusieurs modèles :

```bash
# Modèle léger (2GB, plus rapide)
# Déjà installé : llama3.2:latest

# Modèle équilibré (9GB, recommandé)
# Déjà installé : qwen2.5:14b

# Modèle premium (19GB, meilleur qualité)
# Déjà installé : qwen2.5:32b
```

Puis modifier `OLLAMA_MODEL` dans `.env` selon vos préférences.

## 🧪 Tests

```bash
# Activer l'environnement virtuel
venv\Scripts\activate

# Lancer tous les tests
pytest

# Tests avec coverage
pytest --cov=backend --cov-report=html
```

## 📊 API Documentation

Quand le serveur tourne :
- **Swagger UI** : http://127.0.0.1:8000/docs
- **ReDoc** : http://127.0.0.1:8000/redoc

## 🐛 Dépannage

### Erreur "Ollama non accessible"

```bash
# Vérifier qu'Ollama est lancé :
ollama serve

# Tester l'API :
curl http://localhost:11434/api/tags
```

### Erreur "Port 8000 déjà utilisé"

```bash
# Arrêter le processus existant :
scripts\stop_server.bat

# Ou utiliser un autre port :
uvicorn backend.app.main:app --port 8001
```

### Réinitialiser complètement

```bash
# Supprimer la base de données
del data\lootsandlive.db

# Réinitialiser
scripts\init_db.bat
```

## 🤝 Contribution

Ce projet est actuellement en développement solo. Suggestions bienvenues via Issues.

## 📜 Licence

Propriétaire - © 2025 - Tous droits réservés

## 🙏 Remerciements

- **Ollama** pour l'IA locale
- **FastAPI** pour le framework backend
- **SQLAlchemy** pour l'ORM
- Inspiration : Fallout (Bethesda), Clash of Clans (Supercell)

---

**Version** : 1.0.0-alpha  
**Dernière mise à jour** : 2025-11-07  
**Développeur** : GitHub Copilot  
**PO** : Utilisateur LootsAndLive
