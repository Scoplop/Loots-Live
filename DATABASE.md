# Schéma de Base de Données - Loots&Live

## Vue d'ensemble

**Base de données** : SQLite  
**ORM** : SQLAlchemy 2.0+ (async)  
**Fichier** : `data/lootsandlive.db`

### Tables principales (15 tables)

1. **users** - Comptes joueurs
2. **villages** - Villages des joueurs
3. **characters** - PNJ (joueur + IA)
4. **buildings** - Bâtiments du village
5. **building_instances** - Instances de bâtiments placés
6. **resources** - Stocks de ressources par village
7. **equipment** - Équipements
8. **missions** - Missions en cours/terminées
9. **mission_participants** - PNJ assignés aux missions
10. **researches** - Recherches débloquées
11. **relationships** - Relations PNJ-PNJ
12. **relationship_history** - Historique des changements de relations
13. **events** - Événements du village
14. **villages_ai** - Villages IA
15. **chat_messages** - Messages de chat
16. **squads** - Escouades permanentes
17. **squad_members** - Membres des escouades
18. **achievements** - Achievements des joueurs

---

## Tables détaillées

### 1. users - Comptes joueurs

Stocke les comptes d'authentification.

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    
    -- Contraintes
    CHECK (length(username) >= 3),
    CHECK (length(password_hash) > 0)
);

-- Index
CREATE UNIQUE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

**Colonnes** :
- `id` : ID unique
- `username` : Pseudo (3-20 caractères, unique)
- `email` : Email optionnel (validation format)
- `password_hash` : Hash bcrypt du mot de passe
- `is_active` : Compte actif/banni
- `created_at` : Date de création
- `last_login` : Dernière connexion

**Relations** :
- `1 → N` villages (un user peut avoir plusieurs villages via prestige)

---

### 2. villages - Villages des joueurs

Un village par cycle de prestige.

```sql
CREATE TABLE villages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name VARCHAR(50) NOT NULL,
    level INTEGER DEFAULT 1,
    prestige_cycle INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Position sur la carte du monde
    world_position_x INTEGER DEFAULT 0,
    world_position_y INTEGER DEFAULT 0,
    
    -- Stats globales
    total_buildings INTEGER DEFAULT 0,
    total_characters INTEGER DEFAULT 0,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CHECK (level >= 1 AND level <= 100),
    CHECK (prestige_cycle >= 1 AND prestige_cycle <= 10)
);

-- Index
CREATE INDEX idx_villages_user_id ON villages(user_id);
CREATE INDEX idx_villages_level ON villages(level);
```

**Colonnes** :
- `id` : ID unique
- `user_id` : Propriétaire (FK → users)
- `name` : Nom du village (personnalisable)
- `level` : Niveau moyen du village (1-100)
- `prestige_cycle` : Cycle de prestige actuel (1-10)
- `world_position_x/y` : Position sur carte du monde
- `total_buildings/characters` : Compteurs (dénormalisés pour perfs)

**Relations** :
- `N → 1` users
- `1 → N` characters
- `1 → N` building_instances
- `1 → N` resources
- `1 → N` missions
- `1 → N` events

---

### 3. characters - PNJ (Joueur + IA)

Tous les personnages (PNJ joueur et IA).

```sql
CREATE TABLE characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    village_id INTEGER NOT NULL,
    name VARCHAR(50) NOT NULL,
    is_player BOOLEAN DEFAULT FALSE,
    
    -- Classe (uniquement pour PNJ joueur)
    class VARCHAR(20),  -- 'warrior', 'scout', 'craftsman', 'leader', 'survivor'
    
    -- Personnalité (uniquement pour PNJ IA)
    personality VARCHAR(20),  -- 'friendly', 'shy', 'authoritarian', 'wise', etc.
    personality_prompt TEXT,  -- Prompt IA pré-généré
    
    -- Apparence (JSON stockant les options de customisation)
    appearance_data TEXT NOT NULL,  -- JSON: {sex, hair_style, hair_color, eyes, etc.}
    
    -- Biographie
    biography TEXT,
    
    -- Stats de base (RPG)
    level INTEGER DEFAULT 1,
    experience INTEGER DEFAULT 0,
    strength INTEGER DEFAULT 0,
    dexterity INTEGER DEFAULT 0,
    endurance INTEGER DEFAULT 0,
    speed INTEGER DEFAULT 0,
    intelligence INTEGER DEFAULT 0,
    luck INTEGER DEFAULT 0,
    
    -- Points de stats libres (répartition manuelle)
    free_stat_points INTEGER DEFAULT 0,
    
    -- Santé
    hp_current INTEGER DEFAULT 100,
    hp_max INTEGER DEFAULT 100,
    is_wounded BOOLEAN DEFAULT FALSE,
    wounded_until TIMESTAMP,
    
    -- État
    moral INTEGER DEFAULT 70,  -- 0-100
    fatigue INTEGER DEFAULT 0,  -- 0-100
    
    -- Assignation
    assigned_building_id INTEGER,  -- NULL si disponible
    assigned_squad_id INTEGER,     -- NULL si pas en escouade
    
    -- Dates
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recruited_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Relations familiales
    is_married BOOLEAN DEFAULT FALSE,
    spouse_id INTEGER,
    parent1_id INTEGER,
    parent2_id INTEGER,
    
    FOREIGN KEY (village_id) REFERENCES villages(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_building_id) REFERENCES building_instances(id) ON DELETE SET NULL,
    FOREIGN KEY (assigned_squad_id) REFERENCES squads(id) ON DELETE SET NULL,
    FOREIGN KEY (spouse_id) REFERENCES characters(id) ON DELETE SET NULL,
    FOREIGN KEY (parent1_id) REFERENCES characters(id) ON DELETE SET NULL,
    FOREIGN KEY (parent2_id) REFERENCES characters(id) ON DELETE SET NULL,
    
    CHECK (level >= 1 AND level <= 100),
    CHECK (experience >= 0),
    CHECK (moral >= 0 AND moral <= 100),
    CHECK (fatigue >= 0 AND fatigue <= 100),
    CHECK (hp_current >= 0 AND hp_current <= hp_max)
);

-- Index
CREATE INDEX idx_characters_village_id ON characters(village_id);
CREATE INDEX idx_characters_level ON characters(level);
CREATE INDEX idx_characters_is_player ON characters(is_player);
CREATE INDEX idx_characters_assigned_building ON characters(assigned_building_id);
```

**Colonnes clés** :
- `is_player` : TRUE = PNJ joueur, FALSE = PNJ IA
- `class` : Classe du PNJ joueur (warrior, scout, etc.)
- `personality` : Type de personnalité (PNJ IA uniquement)
- `personality_prompt` : Prompt IA pré-généré à la création
- `appearance_data` : JSON avec toutes les options d'apparence
- Stats : strength, dexterity, endurance, speed, intelligence, luck
- `hp_current/hp_max` : Points de vie
- `is_wounded` : Statut blessé (malus stats)
- `moral` : Moral (affecte production et risque de départ)
- `assigned_building_id` : Bâtiment de travail (NULL = disponible)

**Relations** :
- `N → 1` villages
- `N → 1` building_instances (assignation)
- `1 → N` equipment (portés)
- `N → N` missions (via mission_participants)
- `1 → N` relationships (avec autres PNJ)
- `1 → 1` characters (conjoint)
- `N → 1` characters (parents)

---

### 4. buildings - Types de bâtiments (données statiques)

Table de référence pour les types de bâtiments (données fixes, pas modifiées par le jeu).

```sql
CREATE TABLE buildings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,  -- 'house', 'forge', 'farm', etc.
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,  -- 'base', 'production', 'military', etc.
    
    -- Dimensions
    width INTEGER DEFAULT 2,
    height INTEGER DEFAULT 2,
    
    -- Capacité PNJ
    min_workers INTEGER DEFAULT 0,
    max_workers INTEGER DEFAULT 0,
    
    -- Coûts de construction (niveau 1)
    cost_wood INTEGER DEFAULT 0,
    cost_stone INTEGER DEFAULT 0,
    cost_metal INTEGER DEFAULT 0,
    cost_gold INTEGER DEFAULT 0,
    
    -- Temps de construction (en secondes, niveau 1)
    build_time INTEGER DEFAULT 60,
    
    -- Prérequis
    required_research_id INTEGER,
    
    -- Production/Consommation (JSON par niveau)
    production_data TEXT,  -- JSON: {1: {water: 10}, 2: {water: 15}, ...}
    consumption_data TEXT, -- JSON: {1: {wood: 5}, 2: {wood: 8}, ...}
    
    FOREIGN KEY (required_research_id) REFERENCES researches(id),
    CHECK (width > 0 AND height > 0)
);

-- Index
CREATE UNIQUE INDEX idx_buildings_code ON buildings(code);
```

**Données pré-chargées** : 24 types de bâtiments (Maison, Forge, Ferme, etc.)

---

### 5. building_instances - Instances de bâtiments placés

Bâtiments réellement construits dans un village.

```sql
CREATE TABLE building_instances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    village_id INTEGER NOT NULL,
    building_id INTEGER NOT NULL,
    
    -- Position sur la grille
    position_x INTEGER NOT NULL,
    position_y INTEGER NOT NULL,
    
    -- Niveau actuel
    level INTEGER DEFAULT 1,
    
    -- État
    is_active BOOLEAN DEFAULT TRUE,
    is_under_construction BOOLEAN DEFAULT FALSE,
    construction_started_at TIMESTAMP,
    construction_completed_at TIMESTAMP,
    
    -- Worker assigné à la construction (PNJ constructeur)
    constructor_id INTEGER,
    
    -- Dates
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (village_id) REFERENCES villages(id) ON DELETE CASCADE,
    FOREIGN KEY (building_id) REFERENCES buildings(id),
    FOREIGN KEY (constructor_id) REFERENCES characters(id) ON DELETE SET NULL,
    
    CHECK (level >= 1 AND level <= 10),
    CHECK (position_x >= 0 AND position_y >= 0)
);

-- Index
CREATE INDEX idx_building_instances_village_id ON building_instances(village_id);
CREATE INDEX idx_building_instances_position ON building_instances(village_id, position_x, position_y);
CREATE INDEX idx_building_instances_construction ON building_instances(is_under_construction);
```

**Colonnes clés** :
- `building_id` : Type de bâtiment (FK → buildings)
- `position_x/y` : Position sur grille 50×50
- `level` : Niveau actuel (1-10)
- `is_active` : Actif/en pause
- `is_under_construction` : En construction
- `constructor_id` : PNJ qui construit

**Relations** :
- `N → 1` villages
- `N → 1` buildings (type)
- `1 → N` characters (workers assignés)

---

### 6. resources - Stocks de ressources par village

Stocke les quantités de chaque ressource par village.

```sql
CREATE TABLE resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    village_id INTEGER NOT NULL,
    resource_type VARCHAR(50) NOT NULL,  -- 'water', 'wood', 'stone', etc.
    quantity INTEGER DEFAULT 0,
    capacity INTEGER DEFAULT 1000,  -- Dépend du niveau d'Entrepôt
    
    -- Production/Consommation (par seconde, calculé en temps réel)
    production_rate REAL DEFAULT 0.0,
    consumption_rate REAL DEFAULT 0.0,
    
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (village_id) REFERENCES villages(id) ON DELETE CASCADE,
    CHECK (quantity >= 0),
    CHECK (capacity > 0),
    
    UNIQUE(village_id, resource_type)
);

-- Index
CREATE INDEX idx_resources_village_id ON resources(village_id);
CREATE INDEX idx_resources_type ON resources(resource_type);
```

**Types de ressources** (30 types) :
- **Village** (20) : water, wood, stone, metal, food, wheat, meat, cloth, leather, herb, book, gold, seeds, tools, cotton, linen, paper, ink, rare_ore, knowledge_points
- **Mission** (10) : survival_kit, electronic_component, explosive_powder, gem, resin, armor_plate, fuel, ammunition, mechanical_parts, ancient_relic

**Colonnes clés** :
- `resource_type` : Type de ressource (enum)
- `quantity` : Quantité actuelle
- `capacity` : Capacité max (dépend Entrepôt)
- `production_rate` : Production/seconde (calculé)
- `consumption_rate` : Consommation/seconde (calculé)

---

### 7. equipment - Équipements

Tous les équipements du jeu (craftés ou trouvés).

```sql
CREATE TABLE equipment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    village_id INTEGER NOT NULL,
    
    -- Équipé par qui (NULL = dans inventaire)
    equipped_by_character_id INTEGER,
    
    -- Type et slot
    equipment_type VARCHAR(50) NOT NULL,  -- 'helmet', 'chest', 'weapon', etc.
    slot VARCHAR(20) NOT NULL,  -- 'head', 'torso', 'hands', 'weapon_1', etc.
    
    -- Nom et description
    name VARCHAR(100) NOT NULL,
    description TEXT,
    
    -- Niveau et rareté
    level INTEGER DEFAULT 1,
    rarity VARCHAR(20) NOT NULL,  -- 'common', 'uncommon', 'rare', 'epic', 'legendary', 'mythic'
    
    -- Stats (JSON pour flexibilité)
    stats_data TEXT NOT NULL,  -- JSON: {strength: 10, defense: 5, speed: 3}
    
    -- Score de puissance (calculé)
    power_score INTEGER DEFAULT 0,
    
    -- Origine
    source VARCHAR(50),  -- 'crafted', 'mission', 'trade'
    
    -- Dates
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Visuel (optionnel, pour sprite personnalisé)
    visual_data TEXT,  -- JSON: {sprite_id, color, effects}
    
    FOREIGN KEY (village_id) REFERENCES villages(id) ON DELETE CASCADE,
    FOREIGN KEY (equipped_by_character_id) REFERENCES characters(id) ON DELETE SET NULL,
    
    CHECK (level >= 1 AND level <= 100),
    CHECK (power_score >= 0)
);

-- Index
CREATE INDEX idx_equipment_village_id ON equipment(village_id);
CREATE INDEX idx_equipment_character_id ON equipment(equipped_by_character_id);
CREATE INDEX idx_equipment_rarity ON equipment(rarity);
CREATE INDEX idx_equipment_level ON equipment(level);
```

**Raretés** :
- `common` : Gris, bonus ×1.0
- `uncommon` : Vert, bonus ×1.15
- `rare` : Bleu, bonus ×1.30
- `epic` : Violet, bonus ×1.50
- `legendary` : Orange, bonus ×1.80
- `mythic` : Rouge/Doré, bonus ×2.20

**Slots** :
- head, shoulders, torso, legs, feet, hands
- jewelry_1, jewelry_2, jewelry_3
- weapon_1, weapon_2 (selon classe)

---

### 8. missions - Missions

Missions en cours ou terminées.

```sql
CREATE TABLE missions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    village_id INTEGER NOT NULL,
    
    -- Type et niveau
    mission_type VARCHAR(50) NOT NULL,  -- 'harvest', 'rescue', 'exploration'
    level INTEGER NOT NULL,
    
    -- État
    status VARCHAR(20) DEFAULT 'preparing',  -- 'preparing', 'in_progress', 'completed', 'failed', 'recalled'
    
    -- Timers
    started_at TIMESTAMP,
    expected_completion_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Progression (0-100%)
    progress_percentage INTEGER DEFAULT 0,
    
    -- Ressources consommées
    survival_kits_used INTEGER DEFAULT 0,
    
    -- Calcul de réussite
    required_score INTEGER NOT NULL,
    team_score INTEGER DEFAULT 0,
    success_chance INTEGER DEFAULT 0,  -- Pourcentage (0-100)
    
    -- Résultat (JSON)
    result_data TEXT,  -- JSON: {success: true, rewards: {...}, narrative: "..."}
    
    -- Narration IA
    narrative TEXT,
    
    FOREIGN KEY (village_id) REFERENCES villages(id) ON DELETE CASCADE,
    
    CHECK (level >= 1 AND level <= 100),
    CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    CHECK (success_chance >= 0 AND success_chance <= 100)
);

-- Index
CREATE INDEX idx_missions_village_id ON missions(village_id);
CREATE INDEX idx_missions_status ON missions(status);
CREATE INDEX idx_missions_completion ON missions(expected_completion_at);
```

**Statuts** :
- `preparing` : En préparation (sélection équipe)
- `in_progress` : En cours
- `completed` : Terminée (succès)
- `failed` : Terminée (échec)
- `recalled` : Rappelée prématurément

---

### 9. mission_participants - PNJ assignés aux missions

Table de liaison N-N entre missions et characters.

```sql
CREATE TABLE mission_participants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mission_id INTEGER NOT NULL,
    character_id INTEGER NOT NULL,
    
    -- XP gagnée à la fin
    experience_gained INTEGER DEFAULT 0,
    
    -- Blessures reçues
    damage_taken INTEGER DEFAULT 0,
    was_wounded BOOLEAN DEFAULT FALSE,
    
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    
    UNIQUE(mission_id, character_id)
);

-- Index
CREATE INDEX idx_mission_participants_mission ON mission_participants(mission_id);
CREATE INDEX idx_mission_participants_character ON mission_participants(character_id);
```

---

### 10. researches - Recherches

Recherches débloquées par village.

```sql
CREATE TABLE researches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    village_id INTEGER NOT NULL,
    
    -- Code unique de la recherche
    research_code VARCHAR(50) NOT NULL,  -- 'duo_survival', 'tactical_squad', etc.
    
    -- État
    status VARCHAR(20) DEFAULT 'locked',  -- 'locked', 'available', 'in_progress', 'completed'
    
    -- Timers
    started_at TIMESTAMP,
    expected_completion_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Progression (0-100%)
    progress_percentage INTEGER DEFAULT 0,
    
    FOREIGN KEY (village_id) REFERENCES villages(id) ON DELETE CASCADE,
    
    CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    UNIQUE(village_id, research_code)
);

-- Index
CREATE INDEX idx_researches_village_id ON researches(village_id);
CREATE INDEX idx_researches_status ON researches(status);
```

**Codes de recherche** (40+) : stockés dans constants.py

---

### 11. relationships - Relations PNJ-PNJ

Relations entre personnages.

```sql
CREATE TABLE relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    character_from_id INTEGER NOT NULL,
    character_to_id INTEGER NOT NULL,
    
    -- Valeur de la relation (-100 à +100)
    value INTEGER DEFAULT 0,
    
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (character_from_id) REFERENCES characters(id) ON DELETE CASCADE,
    FOREIGN KEY (character_to_id) REFERENCES characters(id) ON DELETE CASCADE,
    
    CHECK (value >= -100 AND value <= 100),
    CHECK (character_from_id != character_to_id),
    UNIQUE(character_from_id, character_to_id)
);

-- Index
CREATE INDEX idx_relationships_from ON relationships(character_from_id);
CREATE INDEX idx_relationships_to ON relationships(character_to_id);
CREATE INDEX idx_relationships_value ON relationships(value);
```

---

### 12. relationship_history - Historique des relations

Historique des changements de relations pour affichage.

```sql
CREATE TABLE relationship_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    relationship_id INTEGER NOT NULL,
    
    old_value INTEGER NOT NULL,
    new_value INTEGER NOT NULL,
    delta INTEGER NOT NULL,
    
    reason VARCHAR(255) NOT NULL,  -- "Mission réussie ensemble", "Conflit au travail", etc.
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (relationship_id) REFERENCES relationships(id) ON DELETE CASCADE
);

-- Index
CREATE INDEX idx_relationship_history_relationship ON relationship_history(relationship_id);
CREATE INDEX idx_relationship_history_date ON relationship_history(created_at);
```

---

### 13. events - Événements du village

Événements procéduraux générés automatiquement.

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    village_id INTEGER NOT NULL,
    
    -- Type d'événement
    event_type VARCHAR(50) NOT NULL,  -- 'positive', 'negative', 'special'
    event_code VARCHAR(50) NOT NULL,  -- 'feast', 'accident', 'merchant', etc.
    
    -- Narration IA
    narrative TEXT NOT NULL,
    
    -- Effets (JSON)
    effects_data TEXT,  -- JSON: {moral_change: +10, resources: {wood: -50}}
    
    -- PNJ impliqués
    involved_characters TEXT,  -- JSON: [id1, id2, ...]
    
    -- Visualisation
    viewed BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (village_id) REFERENCES villages(id) ON DELETE CASCADE
);

-- Index
CREATE INDEX idx_events_village_id ON events(village_id);
CREATE INDEX idx_events_viewed ON events(viewed);
CREATE INDEX idx_events_date ON events(created_at);
```

**Types d'événements** :
- **Positifs** : feast, discovery, birth, inspiration
- **Négatifs** : accident, theft, disease, departure
- **Spéciaux** : merchant, animal_attack, aurora

---

### 14. villages_ai - Villages IA

Villages contrôlés par l'IA (diplomatie).

```sql
CREATE TABLE villages_ai (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(50) NOT NULL,
    
    -- Score abstrait (pas de simulation complète)
    score INTEGER DEFAULT 100,
    
    -- Niveau moyen estimé
    estimated_level INTEGER DEFAULT 10,
    
    -- Position sur carte du monde
    world_position_x INTEGER NOT NULL,
    world_position_y INTEGER NOT NULL,
    
    -- État
    is_destroyed BOOLEAN DEFAULT FALSE,
    destroyed_at TIMESTAMP,
    
    -- Ressources approximatives (JSON)
    resources_data TEXT,  -- JSON: {water: ~500, wood: ~300}
    
    -- Généré procéduralement (seed pour reproduction)
    generation_seed INTEGER NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CHECK (score >= 0),
    CHECK (estimated_level >= 1 AND estimated_level <= 100)
);

-- Index
CREATE INDEX idx_villages_ai_destroyed ON villages_ai(is_destroyed);
```

**Relations avec joueur** : Stockées dans table séparée `ai_village_relations`.

---

### 15. chat_messages - Messages de chat

Historique de tous les messages (village, bâtiment, privé).

```sql
CREATE TABLE chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    village_id INTEGER NOT NULL,
    
    -- Type de chat
    chat_type VARCHAR(20) NOT NULL,  -- 'village', 'building', 'private'
    
    -- Contexte (selon type)
    building_id INTEGER,  -- Si chat_type = 'building'
    character_from_id INTEGER,  -- Émetteur
    character_to_id INTEGER,    -- Destinataire (si chat_type = 'private')
    
    -- Message
    message TEXT NOT NULL,
    
    -- Généré par IA
    is_ai_generated BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (village_id) REFERENCES villages(id) ON DELETE CASCADE,
    FOREIGN KEY (building_id) REFERENCES building_instances(id) ON DELETE CASCADE,
    FOREIGN KEY (character_from_id) REFERENCES characters(id) ON DELETE CASCADE,
    FOREIGN KEY (character_to_id) REFERENCES characters(id) ON DELETE CASCADE
);

-- Index
CREATE INDEX idx_chat_messages_village_id ON chat_messages(village_id);
CREATE INDEX idx_chat_messages_type ON chat_messages(chat_type);
CREATE INDEX idx_chat_messages_date ON chat_messages(created_at);
```

---

### 16. squads - Escouades permanentes

Escouades configurables (Caserne d'Escouades).

```sql
CREATE TABLE squads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    village_id INTEGER NOT NULL,
    name VARCHAR(50) NOT NULL,
    
    -- Slot (1, 2, ou 3 max)
    slot_number INTEGER NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (village_id) REFERENCES villages(id) ON DELETE CASCADE,
    
    CHECK (slot_number >= 1 AND slot_number <= 3),
    UNIQUE(village_id, slot_number)
);

-- Index
CREATE INDEX idx_squads_village_id ON squads(village_id);
```

---

### 17. squad_members - Membres des escouades

Table de liaison N-N entre squads et characters.

```sql
CREATE TABLE squad_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    squad_id INTEGER NOT NULL,
    character_id INTEGER NOT NULL,
    
    -- Stat prioritaire pour auto-équipement
    priority_stat VARCHAR(20),  -- 'strength', 'dexterity', etc.
    
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (squad_id) REFERENCES squads(id) ON DELETE CASCADE,
    FOREIGN KEY (character_id) REFERENCES characters(id) ON DELETE CASCADE,
    
    UNIQUE(squad_id, character_id)
);

-- Index
CREATE INDEX idx_squad_members_squad ON squad_members(squad_id);
CREATE INDEX idx_squad_members_character ON squad_members(character_id);
```

---

### 18. achievements - Achievements des joueurs

Achievements débloqués.

```sql
CREATE TABLE achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    
    achievement_code VARCHAR(50) NOT NULL,  -- 'first_building', 'level_50', etc.
    
    -- Progression (si achievement progressif)
    current_progress INTEGER DEFAULT 0,
    target_progress INTEGER DEFAULT 1,
    
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    
    UNIQUE(user_id, achievement_code)
);

-- Index
CREATE INDEX idx_achievements_user_id ON achievements(user_id);
CREATE INDEX idx_achievements_completed ON achievements(is_completed);
```

---

## Relations entre tables (Schéma ER)

```
users (1) ──< villages (N)
                │
                ├──< characters (N)
                │    ├──< equipment (N)
                │    ├──< relationships (N) ──< relationship_history (N)
                │    └──< mission_participants (N) ──> missions (1)
                │
                ├──< building_instances (N) ──> buildings (1)
                ├──< resources (N)
                ├──< missions (N)
                ├──< researches (N)
                ├──< events (N)
                ├──< chat_messages (N)
                └──< squads (N) ──< squad_members (N) ──> characters (1)

villages_ai (indépendants)
```

---

## Indexation et optimisations

### Index importants

Tous les index sont déjà définis dans les CREATE TABLE ci-dessus.

**Index critiques pour performances** :
- `users.username` (UNIQUE) - Login
- `villages.user_id` - Récupération village joueur
- `characters.village_id` - Liste PNJ par village
- `characters.assigned_building_id` - Workers d'un bâtiment
- `building_instances.village_id` - Bâtiments d'un village
- `resources.village_id, resource_type` - Stocks de ressources
- `missions.village_id, status` - Missions actives
- `relationships.character_from_id` - Relations d'un PNJ
- `events.village_id, created_at` - Événements récents

### Contraintes d'intégrité

- **CASCADE DELETE** : Suppression d'un village → suppression de tout ce qui lui appartient
- **SET NULL** : Suppression d'un bâtiment → les PNJ assignés deviennent disponibles
- **CHECK** : Validation des ranges (level 1-100, moral 0-100, etc.)

---

## Migrations futures

Pour l'instant, pas de système de migration (Alembic). Si besoin futur :

```bash
# Installer Alembic
pip install alembic

# Initialiser
alembic init alembic

# Créer migration
alembic revision --autogenerate -m "Add new table"

# Appliquer
alembic upgrade head
```

---

**Dernière mise à jour** : 2025-11-07  
**Version** : 1.0  
**Tables** : 18 tables principales
