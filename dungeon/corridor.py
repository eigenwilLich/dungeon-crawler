from .tile import TileType
import logging
from utils.logger_config import logger

logger = logging.getLogger("DungeonGame")

class Corridor:
    existing_corridors = set() # Verhindert doppelte Korridore

    @staticmethod
    def create(dungeon, start, end):
        """
        Erstellt einen L-förmigen Korridor vom Punkt `start` nach `end`.
        Vermeidet doppelte Korridore mithilfe von `existing_corridors`.
        """
        if (start, end) in Corridor.existing_corridors or (end, start) in Corridor.existing_corridors:
            logger.debug("Corridor already exists: %s -> %s", start, end, extra={"category": "corridors"})
            return

        logger.info("Creating corridor: %s -> %s", start, end, extra={"category": "corridors"})

        # Zeichnet zuerst horizontal (X), dann vertikal (Y)
        Corridor._create_horizontal_segment(dungeon, start[0], end[0], start[1])
        Corridor._create_vertical_segment(dungeon, start[1], end[1], end[0])

        # Speichert den neuen Korridor (in beide Richtungen)
        Corridor.existing_corridors.add((start, end))
        Corridor.existing_corridors.add((end, start))
        logger.debug("Corridor successfully created: %s -> %s", start, end, extra={"category": "corridors"})

    @staticmethod
    def _create_horizontal_segment(dungeon, x1, x2, y):
        """
        Zeichnet einen horizontalen Korridor von x1 nach x2 auf der Zeile y.
        """
        for x in range(min(x1, x2), max(x1, x2) + 1):
            dungeon[y][x] = TileType.FLOOR
        logger.debug("Horizontal segment created at y=%d, x1=%d, x2=%d", y, x1, x2, extra={"category": "corridors"})

    @staticmethod
    def _create_vertical_segment(dungeon, y1, y2, x):
        """
        Zeichnet einen vertikalen Korridor von y1 nach y2 in der Spalte x.
        """
        for y in range(min(y1, y2), max(y1, y2) + 1):
            dungeon[y][x] = TileType.FLOOR
        logger.debug("Vertical segment created at x=%d, y1=%d, y2=%d", x, y1, y2, extra={"category": "corridors"})

    @staticmethod
    def reset_corridors():
        """
        Setzt die gespeicherten Korridore zurück (z. B. beim Neugenerieren eines Dungeons).
        """
        Corridor.existing_corridors.clear()
        logger.info("All corridors reset.", extra={"category": "corridors"})
