import logging

# Logger konfigurieren
logger = logging.getLogger("DungeonGame")

def print_dungeon(dungeon):
    """Zeigt die Dungeon-Karte in der Konsole an."""
    logger.info("Dungeon layout:", extra={"category": "levels"})
    for row in dungeon:
        logger.debug("".join(str(tile) for tile in row), extra={"category": "levels"})

def print_staircase_positions(staircase_up, staircase_down):
    if staircase_up:
        logger.info(f"Staircase Up: ({staircase_up[0]}, {staircase_up[1]})", extra={"category": "stairs"})
    else:
        logger.warning("Staircase Up: None", extra={"category": "stairs"})
    
    if staircase_down:
        logger.info(f"Staircase Down: ({staircase_down[0]}, {staircase_down[1]})", extra={"category": "stairs"})
    else:
        logger.warning("Staircase Down: None", extra={"category": "stairs"})
