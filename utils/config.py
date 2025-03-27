# Konstanten
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
TILE_SIZE = 30

DUNGEON_PARAMS = {
    "width": 75,
    "height": 75,
    "min_rooms": 15,
    "max_rooms": 20,
    "room_size_range": (8, 14),
    "seed": None,  # None für zufällige Ergebnisse
}

MINIMAP_SIZE = (200, 200)

# Farben als Konstanten
COLORS = {
    "FLOOR_COLOR": (30, 60, 30),
    "WALL_COLOR": (85, 107, 47),
    "STAIRS_DOWN_COLOR": (255, 0, 0),
    "STAIRS_UP_COLOR": (0, 255, 0),
    "PLAYER_COLOR": (255, 255, 255)
}

# Skillbar-Einstellungen
SKILLBAR_WIDTH = 300  # Gesamtbreite
SKILLBAR_HEIGHT = 50  # Höhe der Skillbar
SKILL_SLOT_SIZE = 50  # Größe der einzelnen Slots
SKILL_SPACING = 10  # Abstand zwischen Slots
SKILLBAR_Y_OFFSET = 20  # Abstand vom unteren Bildschirmrand