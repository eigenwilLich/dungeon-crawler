import logging
from dungeon.tile import TileType
from utils.logger_config import logger
from .stats import Stats

class Player:
    def __init__(self, x, y, size, speed, stats=None):
        self.x = x
        self.y = y
        self.size = size
        self.speed = speed
        self.max_health = 100
        self.current_health = 100
        self.max_resource = 50
        self.current_resource = 50
        self.stats = stats or Stats()

         # Fähigkeiten-Management
        self.skills = [
            {"name": "Feuerball", "icon": None, "cooldown": 5},
            {"name": "Heilung", "icon": None, "cooldown": 10},
            {"name": "Sprint", "icon": None, "cooldown": 3},
            {"name": "Schutzschild", "icon": None, "cooldown": 8},
            {"name": "Bodenstampfer", "icon": None, "cooldown": 6},
        ]
        self.skill_cooldowns = [0] * len(self.skills)  # Anfangs sind alle Fähigkeiten bereit

    def move(self, delta_x, delta_y, dungeon, tile_size):
        """Bewegt den Spieler, wenn das Ziel passierbar ist."""
        new_x = self.x + delta_x
        new_y = self.y + delta_y

        # Prüfe, ob die neue Position für beide Achsen passierbar ist
        if self._can_move(new_x, self.y, dungeon, tile_size):
            self.x = new_x
        if self._can_move(self.x, new_y, dungeon, tile_size):
            self.y = new_y

    def _can_move(self, x, y, dungeon, tile_size):
        """Überprüft, ob der Spieler sich bewegen kann (Kollisionsabfrage)."""
        corners = [
            (x, y),
            (x + self.size, y),
            (x, y + self.size),
            (x + self.size, y + self.size)
        ]

        for corner_x, corner_y in corners:
            tile_x = int(corner_x // tile_size)
            tile_y = int(corner_y // tile_size)

            if not (0 <= tile_x < len(dungeon[0]) and 0 <= tile_y < len(dungeon)):
                return False

            if dungeon[tile_y][tile_x] not in [TileType.FLOOR, TileType.STAIRS_UP, TileType.STAIRS_DOWN]:
                return False

        return True
    
    def get_position_in_tiles(self, tile_size):
        """Gibt die Position des Spielers in Dungeon-Tiles zurück."""
        return self.x // tile_size, self.y // tile_size
    
    def take_damage(self, amount):
        """Fügt dem Spieler Schaden zu."""
        self.current_health = max(0, self.current_health - amount)
        if self.current_health == 0:
            self.on_death()

    def heal(self, amount):
        """Heilt den Spieler."""
        self.current_health = min(self.max_health, self.current_health + amount)

    def on_death(self):
        """Wird aufgerufen, wenn der Spieler stirbt."""
        logger.info("Player is dead!", extra={"category": "player"})

    def use_skill(self, skill_number):
        """Verwendet eine Kampffertigkeit basierend auf der Tastenbelegung."""
        logger.info("Player used skill %d", skill_number, extra={"category": "skills"})

    def open_character_menu(self):
        """Öffnet das Charakter- und Inventar-Menü."""
        logger.info("Character menu opened.", extra={"category": "menu"})

