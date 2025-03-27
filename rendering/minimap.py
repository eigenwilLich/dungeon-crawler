import pygame
import logging
from dungeon.tile import TileType
from utils.config import TILE_SIZE, COLORS

logger = logging.getLogger("DungeonGame")

def draw_minimap(surface, dungeon, player_x, player_y, minimap_size):
    """Zeichnet die Minimap korrekt, ohne doppelte Rahmen oder überflüssige Zeichnungen."""
    if not dungeon:
        print("FEHLER: Dungeon-Daten fehlen!")
        return

    minimap_width, minimap_height = minimap_size
    dungeon_width, dungeon_height = len(dungeon[0]), len(dungeon)
    scale_x, scale_y = minimap_width / dungeon_width, minimap_height / dungeon_height

    # **Minimap-Position**
    minimap_x, minimap_y = surface.get_width() - minimap_width - 20, 20

    # **Erstelle eine separate Minimap-Oberfläche**
    minimap_surface = pygame.Surface((minimap_width, minimap_height), pygame.SRCALPHA)
    minimap_surface.fill((20, 20, 20, 180))  # Dunkelgrau, leicht transparent

    # **Dungeon-Kacheln zeichnen**
    tile_colors = {
        TileType.FLOOR: COLORS["FLOOR_COLOR"],
        TileType.WALL: COLORS["WALL_COLOR"],
        TileType.STAIRS_DOWN: COLORS["STAIRS_DOWN_COLOR"],
        TileType.STAIRS_UP: COLORS["STAIRS_UP_COLOR"]
    }

    for y, row in enumerate(dungeon):
        for x, tile in enumerate(row):
            rect = pygame.Rect(
                round(x * scale_x),
                round(y * scale_y),
                max(1, round(scale_x)),  # Mindestgröße von 1 Pixel
                max(1, round(scale_y))
            )
            color = tile_colors.get(tile, COLORS.get("BACKGROUND_COLOR", (0, 0, 0)))
            pygame.draw.rect(minimap_surface, color, rect)

    # **Spielerposition zeichnen**
    player_tile_x, player_tile_y = int(player_x / TILE_SIZE), int(player_y / TILE_SIZE)
    if 0 <= player_tile_x < dungeon_width and 0 <= player_tile_y < dungeon_height:
        player_minimap_x, player_minimap_y = round(player_tile_x * scale_x), round(player_tile_y * scale_y)
        player_rect = pygame.Rect(player_minimap_x, player_minimap_y, max(1, round(scale_x)), max(1, round(scale_y)))
        pygame.draw.rect(minimap_surface, COLORS["PLAYER_COLOR"], player_rect)

    # **Minimap nur EINMAL auf den Hauptbildschirm zeichnen**
    surface.blit(minimap_surface, (minimap_x, minimap_y))

    # **Weiße Umrandung um die Minimap**
    pygame.draw.rect(surface, (255, 255, 255), (minimap_x - 1, minimap_y - 1, minimap_width + 2, minimap_height + 2), 2)

    # **Debugging**
    #print(f"DEBUG: Minimap bei ({minimap_x}, {minimap_y}) mit Größe {minimap_width}x{minimap_height}")
