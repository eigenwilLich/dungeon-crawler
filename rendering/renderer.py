import pygame
import logging  # Füge das fehlende Logging-Modul hinzu
from dungeon.tile import TileType
from utils.logger_config import logger
from entities.player import Player

logger = logging.getLogger("DungeonGame")  # Nutze den zentral konfigurierten Logger


class Renderer:
    """Verantwortlich für das Zeichnen des Dungeons und des Spielers auf dem Bildschirm."""
    FLOOR_COLOR = (30, 60, 30)  # Farbe für Boden
    WALL_COLOR = (85, 107, 47)  # Farbe für Wand
    STAIRS_DOWN_COLOR = (255, 0, 0)  # Farbe für Treppe nach unten
    STAIRS_UP_COLOR = (0, 255, 0)  # Farbe für Treppe nach oben
    BACKGROUND_COLOR = (0, 0, 0)  # Farbe für Hintergrund
    PLAYER_COLOR = (255, 255, 255)  # Farbe für den Spieler

    def __init__(self, tile_size):
        self.tile_size = tile_size

    def render(self, screen, dungeon, camera_offset_x, camera_offset_y):
        """
        Zeichnet alle Tiles des Dungeons auf Basis des Kamera-Offsets.
        """
        for y, row in enumerate(dungeon):
            for x, tile in enumerate(row):
                screen_x = x * self.tile_size - camera_offset_x
                screen_y = y * self.tile_size - camera_offset_y
                rect = pygame.Rect(screen_x, screen_y, self.tile_size, self.tile_size)
                
                # Bestimmt die Farbe basierend auf dem TileType
                color = {
                    TileType.FLOOR: self.FLOOR_COLOR,
                    TileType.WALL: self.WALL_COLOR,
                    TileType.STAIRS_DOWN: self.STAIRS_DOWN_COLOR,
                    TileType.STAIRS_UP: self.STAIRS_UP_COLOR,
                }.get(tile, self.BACKGROUND_COLOR)  # Fallback auf Hintergrundfarbe
                
                pygame.draw.rect(screen, color, rect)
                # Korrektes Logging ohne fehlerhafte Felder
                #logger.debug("Tile: %s, Screen Position: (%d, %d)", tile, screen_x, screen_y)

    def draw_player(self, screen, player_x, player_y, player_size, camera_offset_x, camera_offset_y):
        """
        Zeichnet den Spieler auf den Bildschirm.

        Args:
            screen (pygame.Surface): Die Oberfläche, auf die der Spieler gezeichnet wird.
            player_x (float): Spielerposition in X-Richtung (Pixel).
            player_y (float): Spielerposition in Y-Richtung (Pixel).
            player_size (int): Die Größe des Spielers in Pixeln.
            camera_offset_x (float): Kamera-Offset in X-Richtung.
            camera_offset_y (float): Kamera-Offset in Y-Richtung.
        """
        screen_x = player_x - camera_offset_x
        screen_y = player_y - camera_offset_y
        player_rect = pygame.Rect(screen_x, screen_y, player_size, player_size)
        pygame.draw.rect(screen, self.PLAYER_COLOR, player_rect)

    import pygame

def draw_character_ui(screen, player):
    """Zeichnet das Charakterbild, Lebensbalken und Ressourcenbalken."""
    # Dimensionen und Positionen
    ui_x = 20  # Abstand vom linken Bildschirmrand
    ui_y = 20  # Abstand vom oberen Bildschirmrand
    bar_width = 200  # Breite der Lebens- und Ressourcenbalken
    bar_height = 20  # Höhe eines Balkens
    padding = 5  # Abstand zwischen den Balken
    character_size = bar_height * 2 + padding  # Höhe des Charakterbilds (2 Balken + Abstand)

    # Charakter-Bild zeichnen
    character_image = pygame.Surface((character_size, character_size))
    character_image.fill((150, 150, 150))  # Platzhalter-Farbe für das Bild
    screen.blit(character_image, (ui_x, ui_y))

    # Lebensbalken zeichnen
    health_ratio = player.current_health / player.max_health
    health_bar_rect = pygame.Rect(ui_x + character_size + 10, ui_y, bar_width, bar_height)
    pygame.draw.rect(screen, (255, 0, 0), health_bar_rect)  # Hintergrund (Rot)
    pygame.draw.rect(screen, (0, 255, 0), 
                     pygame.Rect(health_bar_rect.x, health_bar_rect.y, health_bar_rect.width * health_ratio, health_bar_rect.height))  # Vordergrund (Grün)

    # Ressourcenbalken zeichnen
    resource_ratio = player.current_resource / player.max_resource
    resource_bar_rect = pygame.Rect(ui_x + character_size + 10, ui_y + bar_height + padding, bar_width, bar_height)
    pygame.draw.rect(screen, (50, 50, 255), resource_bar_rect)  # Hintergrund (Dunkelblau)
    pygame.draw.rect(screen, (0, 0, 255), 
                     pygame.Rect(resource_bar_rect.x, resource_bar_rect.y, resource_bar_rect.width * resource_ratio, resource_bar_rect.height))  # Vordergrund (Hellblau)

    # Optional: Werte auf die Balken schreiben
    font = pygame.font.Font(None, 24)
    health_text = font.render(f"{player.current_health}/{player.max_health}", True, (255, 255, 255))
    resource_text = font.render(f"{player.current_resource}/{player.max_resource}", True, (255, 255, 255))
    screen.blit(health_text, (health_bar_rect.x + 5, health_bar_rect.y + 2))
    screen.blit(resource_text, (resource_bar_rect.x + 5, resource_bar_rect.y + 2))

def draw_inventory_ui(screen, stats_visible, stats, char_slots, char_area_y, char_area_height, slot_size):
    """Zeichnet das Inventar- und Charakterfenster mit nicht freigeschalteten Slots sowie die Stats, falls sichtbar."""
    logger.debug("draw_inventory_ui called.", extra={"category": "ui"})

    # Fonts einmal definieren
    font_title = pygame.font.Font(None, 36)
    font_button = pygame.font.Font(None, 24)
    font_slot = pygame.font.Font(None, 14)

    # Fenstergrößen und Positionen
    window_width = 800
    window_height = 600
    window_x = (screen.get_width() - window_width) // 2
    window_y = (screen.get_height() - window_height) // 2

    # Fensterhintergrund
    pygame.draw.rect(screen, (30, 30, 30), (window_x, window_y, window_width, window_height))
    pygame.draw.rect(screen, (200, 200, 200), (window_x, window_y, window_width, window_height), 4)

    # Charakterbereich
    char_area_width = (window_width - 60) // 2
    char_area_height = window_height - 40
    char_area_x = window_x + 20
    char_area_y = window_y + 20
    pygame.draw.rect(screen, (50, 50, 50), (char_area_x, char_area_y, char_area_width, char_area_height))
    pygame.draw.rect(screen, (255, 255, 255), (char_area_x, char_area_y, char_area_width, char_area_height), 2)

    # Inventarbereich
    inv_area_width = (window_width - 60) // 2
    inv_area_height = window_height - 40
    inv_area_x = char_area_x + char_area_width + 20
    inv_area_y = char_area_y
    pygame.draw.rect(screen, (50, 50, 50), (inv_area_x, inv_area_y, inv_area_width, inv_area_height))
    pygame.draw.rect(screen, (255, 255, 255), (inv_area_x, inv_area_y, inv_area_width, inv_area_height), 2)

    # Inventar-Titel
    inv_text = font_title.render("Inventar", True, (255, 255, 255))
    screen.blit(inv_text, (inv_area_x + 10, inv_area_y + 10))

    # Charakterslots
    slot_size = 50
    slot_margin = 10

    # Berechnung der Inventar-Slots für Zentrierung
    inv_slots_per_row = 6
    total_slot_width = inv_slots_per_row * (slot_size + slot_margin) - slot_margin
    start_x = inv_area_x + (inv_area_width - total_slot_width) // 2
    max_rows = (inv_area_height - 70) // (slot_size + slot_margin)

    # Zeichne Inventarslots
    unlocked_slots = 24
    for row in range(max_rows):
        for col in range(inv_slots_per_row):
            slot_index = row * inv_slots_per_row + col + 1
            slot_x = start_x + col * (slot_size + slot_margin)
            slot_y = inv_area_y + row * (slot_size + slot_margin) + 50

            if slot_y + slot_size > inv_area_y + inv_area_height - 20:
                break

            # Farbe basierend auf Freischaltungsstatus
            if slot_index <= unlocked_slots:
                slot_color = (70, 70, 70)  # Freigeschaltet
                border_color = (255, 255, 255)
                text_color = (255, 255, 255)
            else:
                slot_color = (40, 40, 40)  # Nicht freigeschaltet
                border_color = (100, 100, 100)
                text_color = (150, 150, 150)  # Ausgegraute Schriftfarbe

            # Zeichne den Slot
            pygame.draw.rect(screen, slot_color, (slot_x, slot_y, slot_size, slot_size))
            pygame.draw.rect(screen, border_color, (slot_x, slot_y, slot_size, slot_size), 2)

            # Slot-Beschriftung
            slot_label = font_slot.render(f"{slot_index}", True, text_color)
            label_x = slot_x + (slot_size - slot_label.get_width()) // 2
            label_y = slot_y + (slot_size - slot_label.get_height()) // 2
            screen.blit(slot_label, (label_x, label_y))

    # Charakterbild
    scaling_factor = 1.4
    model_width = int((char_area_width // 3) * scaling_factor)
    model_height = int(model_width * 1.5)
    model_x = char_area_x + (char_area_width - model_width) // 2
    model_y = char_area_y * 2 - 30

    pygame.draw.rect(screen, (100, 100, 100), (model_x, model_y, model_width, model_height))
    pygame.draw.rect(screen, (255, 255, 255), (model_x, model_y, model_width, model_height), 2)

     # Slot-Größe und Abstand
    slot_size = 70
    slot_margin = 20

    # Charakter-Slot-Berechnung
    model_width = char_area_width // 3
    model_height = int(model_width * 1.5)
    model_x = char_area_x + (char_area_width - model_width) // 2
    model_y = char_area_y + (char_area_height - model_height) // 2

    # Anordnung der Slots innerhalb des Containers
    char_slots = {
        "Kopf": (model_x + model_width // 2 + 6 - slot_size - slot_margin, model_y - slot_size - 107),
        "Hals": (model_x + model_width // 2 - 6 + slot_margin, model_y - slot_size - 107),
        "Schulter Links": (model_x - slot_size - slot_margin -20 , model_y - slot_size - 28),
        "Schulter Rechts": (model_x + model_width + slot_margin + 20, model_y - slot_size - 28),
        "Brust": (model_x + model_width + slot_margin + 20, model_y - 3),
        "Beine": (model_x - slot_size - slot_margin - 20, model_y - 3),
        "Ring 1": (model_x - slot_size - slot_margin -20, model_y + slot_size + slot_margin * 1.5 - 10),
        "Ring 2": (model_x + model_width + slot_margin + 20, model_y + slot_size + slot_margin * 1.5 - 10),
        "Gürtel": (model_x + model_width // 2 - slot_size * 3 // 2 - slot_margin, model_y + model_height -15),
        "Hände": (model_x + model_width // 2 - slot_size // 2, model_y + model_height -15),
        "Füße": (model_x + model_width // 2 + slot_size // 2 + slot_margin, model_y + model_height -15),
        "Waffe": (model_x + model_width // 2 + 10 - slot_size - slot_margin, model_y + model_height + slot_size - 5),
        "Nebenhand": (model_x + model_width // 2 - 10 + slot_margin, model_y + model_height + slot_size - 5),
    }

    # Zeichnen der Slots
    font = pygame.font.Font(None, 14)  # Schriftgröße für Slot-Beschriftungen
    for slot_name, (slot_x, slot_y) in char_slots.items():
        pygame.draw.rect(screen, (70, 70, 70), (slot_x, slot_y, slot_size, slot_size))
        pygame.draw.rect(screen, (255, 255, 255), (slot_x, slot_y, slot_size, slot_size), 2)

        if " " in slot_name or slot_name == "Nebenhand":
            # Mehrzeilige Beschriftung
            words = slot_name.split(" ")
            if slot_name == "Nebenhand":
                words = ["Neben", "hand"]

            for i, word in enumerate(words):
                slot_label = font.render(word, True, (255, 255, 255))
                label_x = slot_x + (slot_size - slot_label.get_width()) // 2
                label_y = slot_y + (slot_size // 2 - len(words) * 8) + i * 16
                screen.blit(slot_label, (label_x, label_y))
        else:
            # Einzeilige Beschriftung
            slot_label = font.render(slot_name, True, (255, 255, 255))
            label_x = slot_x + (slot_size - slot_label.get_width()) // 2
            label_y = slot_y + (slot_size - slot_label.get_height()) // 2
            screen.blit(slot_label, (label_x, label_y))
    
    # Stats-Button
    button_width = 100
    button_height = 40

    # Positionen der Slots "Waffe" und "Nebenhand"
    waffe_x, waffe_y = char_slots["Waffe"]
    nebenhand_x, nebenhand_y = char_slots["Nebenhand"]
    button_width, button_height = 100, 40

    # X-Position: Mitte zwischen "Waffe" und "Nebenhand"
    button_x = waffe_x + (nebenhand_x - waffe_x) // 2 - button_width // 3 + 20

    # Y-Position: Mitte zwischen Slots und Container-Unterkante
    container_bottom = char_area_y + char_area_height
    button_y = waffe_y + slot_size + (container_bottom - (waffe_y + slot_size)) // 2 - button_height // 2

    # Button zeichnen
    pygame.draw.rect(screen, (70, 70, 70), (button_x, button_y, button_width, button_height))
    pygame.draw.rect(screen, (255, 255, 255), (button_x, button_y, button_width, button_height), 2)

    # Button-Beschriftung
    button_text = font_button.render("Stats", True, (255, 255, 255))
    text_x = button_x + (button_width - button_text.get_width()) // 2
    text_y = button_y + (button_height - button_text.get_height()) // 2
    screen.blit(button_text, (text_x, text_y))

    # Erweiterter Stats-Bereich (wenn sichtbar)
    if stats_visible:
        stats_area_width = 300  # Breite des Stats-Bereichs
        stats_area_height = char_area_height  # Gleiche Höhe wie der Charakterbereich
        stats_area_x = char_area_y - stats_area_width - 10  # Links neben dem Charakterbereich
        stats_area_y = char_area_y  # Gleicher Y-Wert wie der Charakterbereich

        # Stats-Bereich zeichnen
        pygame.draw.rect(screen, (50, 50, 50), (stats_area_x, stats_area_y, stats_area_width, stats_area_height))
        pygame.draw.rect(screen, (255, 255, 255), (stats_area_x, stats_area_y, stats_area_width, stats_area_height), 2)

        # Zeichne die Stats
        draw_stats(screen, stats_area_x, stats_area_y, stats_area_width, stats_area_height, stats)

    return char_slots


def draw_stats(screen, stats_area_x, stats_area_y, stats_area_width, stats_area_height, stats):
    """Zeichnet die Stats nach Kategorien geordnet."""
    if not stats_area_width or not stats_area_height:
        logger.error("Stats area dimensions are not defined!")
        return
    
    try:
        font = pygame.font.Font(None, 24)
        start_y = stats_area_y + 20
        line_height = 30

        for category, category_stats in stats.items():
            category_text = font.render(f"=== {category} ===", True, (255, 255, 255))
            screen.blit(category_text, (stats_area_x + 10, start_y))
            start_y += line_height

            for stat_name, stat_value in category_stats.items():
                stat_text = font.render(f"{stat_name}: {stat_value}", True, (255, 255, 255))
                screen.blit(stat_text, (stats_area_x + 20, start_y))
                start_y += line_height
    except Exception as e:
        logger.exception("Error in draw_stats: %s", e, extra={"category": "ui"})


# Skillbar-Einstellungen
SKILLBAR_WIDTH = 300  # Gesamtbreite
SKILLBAR_HEIGHT = 50  # Höhe der Skillbar
SKILL_SLOT_SIZE = 50  # Größe der einzelnen Slots
SKILL_SPACING = 10  # Abstand zwischen Slots
SKILLBAR_Y_OFFSET = 20  # Abstand vom unteren Bildschirmrand


def draw_skillbar(screen, skills, cooldowns):
    """Zeichnet eine moderne, transparente Skillbar mit Schatten, Umrandung und abgerundeten Ecken."""
    screen_width, screen_height = screen.get_size()
    
    # **Skillbar-Parameter**
    padding = 10  # Abstand innerhalb der Skillbar
    slot_size = 50  # Größe der einzelnen Slots
    spacing = 10  # Abstand zwischen den Slots
    skill_count = len(skills)  # Anzahl der Skill-Slots

    # **Gesamtbreite & Höhe der Skillbar**
    total_width = (skill_count * slot_size) + ((skill_count - 1) * spacing) + (2 * padding)
    total_height = slot_size + (2 * padding)

    # **Position der Skillbar (zentriert unten)**
    skillbar_x = (screen_width - total_width) // 2
    skillbar_y = screen_height - total_height - 20  # 20px Abstand vom unteren Rand

    # **Skillbar-Oberfläche mit Transparenz und abgerundeten Ecken**
    skillbar_surface = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
    skillbar_surface.fill((0, 0, 0, 0))  # Vollständig transparent
    pygame.draw.rect(skillbar_surface, (30, 30, 30, 180), (0, 0, total_width, total_height), border_radius=12)

    # **Skillbar auf den Bildschirm blitten**
    screen.blit(skillbar_surface, (skillbar_x, skillbar_y))

    # **Weiße, sanfte Umrandung um die Skillbar (auch abgerundet)**
    pygame.draw.rect(screen, (255, 255, 255, 180), (skillbar_x, skillbar_y, total_width, total_height), 3, border_radius=12)

    # **Schriftart für Zahlen**
    font = pygame.font.Font(None, 24)

    # **Slots zeichnen**
    for i, skill in enumerate(skills):
        slot_x = skillbar_x + padding + i * (slot_size + spacing)
        slot_rect = pygame.Rect(slot_x, skillbar_y + padding, slot_size, slot_size)

        # **Slot-Hintergrund (leicht transparent)**
        pygame.draw.rect(screen, (80, 80, 80, 180), slot_rect, border_radius=8)

        # **Weiße Umrandung um den Slot**
        pygame.draw.rect(screen, (255, 255, 255, 200), slot_rect, 2, border_radius=8)

        # **Skill-Icon zeichnen (falls vorhanden)**
        if skill["icon"]:
            screen.blit(skill["icon"], slot_rect.topleft)

        # **Cooldown-Overlay zeichnen (falls aktiv)**
        if cooldowns[i] > 0:
            overlay = pygame.Surface((slot_size, slot_size), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))  # Halbtransparentes Schwarz
            screen.blit(overlay, slot_rect.topleft)

            # **Cooldown-Zahl anzeigen**
            cooldown_text = font.render(str(int(cooldowns[i])), True, (255, 255, 255))
            screen.blit(cooldown_text, (slot_x + 15, skillbar_y + padding + 10))

        # **Tastenbelegung (1-5) oben rechts im Slot zeichnen**
        key_number = str(i + 1)  # Taste 1-5
        text_surface = font.render(key_number, True, (255, 255, 255))

        # **Position oben rechts im Slot**
        text_x = slot_x + slot_size - text_surface.get_width() - 3
        text_y = skillbar_y + padding + 3

        screen.blit(text_surface, (text_x, text_y))  # Zeichne die Zahl





