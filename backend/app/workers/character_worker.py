"""
Worker pour la régénération automatique des HP des personnages.
Régénère 1% des HP max toutes les 10 minutes pour tous les PNJ vivants.
"""

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.database import AsyncSessionLocal
from backend.app.models.character import Character
from backend.app.services.character_service import CharacterService
from backend.app.utils.constants import calculate_max_hp

logger = logging.getLogger(__name__)


async def regenerate_hp():
    """
    Worker qui régénère les HP de tous les personnages vivants.
    +1% HP max toutes les 10 minutes.
    Les PNJ en mission ne régénèrent pas (en danger).
    """
    async with AsyncSessionLocal() as db:
        try:
            # Récupérer tous les PNJ vivants (HP > 0) et non en mission
            result = await db.execute(
                select(Character).where(
                    Character.current_hp > 0,
                    Character.current_hp < Character.max_hp,
                    Character.on_mission == False
                )
            )
            characters = list(result.scalars().all())
            
            if not characters:
                logger.debug("Aucun personnage à régénérer")
                return
            
            logger.info(f"💚 Régénération HP de {len(characters)} personnage(s)")
            
            character_service = CharacterService(db)
            regenerated_count = 0
            total_hp_restored = 0
            
            for character in characters:
                try:
                    # Calculer 1% des HP max
                    max_hp = calculate_max_hp(character.level, character.endurance)
                    regen_amount = max(1, int(max_hp * 0.01))  # Minimum 1 HP
                    
                    # Régénérer (ne peut pas dépasser HP max)
                    new_hp = min(character.current_hp + regen_amount, max_hp)
                    hp_gained = new_hp - character.current_hp
                    
                    if hp_gained > 0:
                        character.current_hp = new_hp
                        character.max_hp = max_hp  # Update au cas où stats ont changé
                        regenerated_count += 1
                        total_hp_restored += hp_gained
                        
                        logger.debug(
                            f"💚 {character.name}: {character.current_hp - hp_gained} → "
                            f"{character.current_hp} HP (+{hp_gained})"
                        )
                
                except Exception as e:
                    logger.error(f"Erreur régénération HP personnage {character.id}: {e}")
            
            # Sauvegarder tous les changements
            await db.commit()
            
            logger.info(
                f"📊 Régénération terminée: {regenerated_count} personnage(s), "
                f"{total_hp_restored} HP restaurés au total"
            )
        
        except Exception as e:
            logger.error(f"Erreur worker regenerate_hp: {e}")
            await db.rollback()
            raise
