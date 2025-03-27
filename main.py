import pygame 
import random
import logging
import time
from dungeon.dungeon import Dungeon
from rendering.renderer import Renderer, draw_character_ui, draw_inventory_ui, draw_skillbar
from rendering.camera import Camera
from entities.player import Player
from rendering.minimap import draw_minimap
from utils.helpers import print_staircase_positions
from utils.logger_config import logger
from entities.stats import Stats
from menu import Menu
from utils.config import SCREEN_HEIGHT, SCREEN_WIDTH, DUNGEON_PARAMS, TILE_SIZE, MINIMAP_SIZE, FPS

# Logger konfigurieren
logger = logging.getLogger("DungeonGame")

# Globale Variablen zur Verwaltung der Dungeon-Ebenen
dungeons = []               # Liste der bisher generierten Dungeons (mehrere Ebenen)
current_level_index = 0     # Aktuelle Ebene im Dungeon
current_dungeon = None      # Referenz auf das aktuell aktive Dungeon-Objekt

# Timing für Treppen-Nutzung
last_stair_use_time = 0
stair_debounce_time = 0.5   # Zeit in Sekunden zwischen zwei erlaubten Treppennutzungen

# Pygame initialisieren und Fenster erstellen
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dungeon Crawler")
font = pygame.font.Font(None, 36)
clock = pygame.time.Clock()

# Status für UI-Anzeigen
inventory_open = False
stats_visible = False
f_key_pressed = False
last_f_press_time = 0  # Globale Variable für F-Tasten-Debounce
debounce_duration = 0.2  # Zeit in Sekunden zwischen F-Tastendrücken

# Menü erstellen
menu = Menu(screen, font)

# Spielstatus
game_state = "menu" 
running = True

dungeon = None
player = None
renderer = None
camera = None

dungeons = []
current_level_index = 0


def initialize_game() -> tuple:
    """Initialisiert Dungeon, Spieler, Kamera und Renderer für eine neue Ebene."""
    global current_dungeon

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    # Dungeon generieren
    dungeon = Dungeon(
        width=DUNGEON_PARAMS["width"],
        height=DUNGEON_PARAMS["height"],
        min_rooms=DUNGEON_PARAMS["min_rooms"],
        max_rooms=DUNGEON_PARAMS["max_rooms"],
        room_size_range=DUNGEON_PARAMS["room_size_range"],
        seed=DUNGEON_PARAMS["seed"],
    )
    dungeon.generate(start_level=True)
    current_dungeon = dungeon

    # Validierung: Wurden Räume erzeugt?
    if not current_dungeon.rooms:
        logger.error("Dungeon generation failed. No rooms were created.", extra={"category": "levels"})
        raise ValueError("Dungeon generation failed. No rooms were created.")

    logger.info("Dungeon generated with %d rooms", len(current_dungeon.rooms), extra={"category": "summary"})

    # Startposition des Spielers: zufällig innerhalb des Start-Raums
    start_room = current_dungeon.get_start_room()
    if start_room is None:
        raise ValueError("Start room not defined. Dungeon generation failed.")

    x_min, y_min = start_room.x, start_room.y
    x_max, y_max = start_room.x + start_room.width - 1, start_room.y + start_room.height - 1

    player_x = random.randint(x_min, x_max) * TILE_SIZE
    player_y = random.randint(y_min, y_max) * TILE_SIZE

    # Spielerobjekt erstellen
    player = Player(x=player_x, y=player_y, size=20, speed=200, stats=Stats())

    logger.info("Player start position: (%d, %d)", player.x, player.y, extra={"category": "summary"})

    # Renderer und Kamera initialisieren
    renderer = Renderer(TILE_SIZE)
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    return screen, clock, dungeon, player, renderer, camera


def save_current_dungeon():
    """Speichert den aktuellen Zustand des Dungeons in der globalen dungeons-Liste."""
    global current_dungeon  # Muss global sein, um korrekt verändert zu werden

    if current_dungeon is None:
        logger.error("Cannot save dungeon: current_dungeon is None!", extra={"category": "errors"})
        return

    # Bestehenden Zustand überschreiben oder anhängen
    if current_level_index < len(dungeons):
        dungeons[current_level_index] = current_dungeon.save_state()
    else:
        dungeons.append(current_dungeon.save_state())


def load_dungeon(index):
    """Lädt einen gespeicherten Dungeon-Zustand anhand seines Index."""
    global current_dungeon

    if index < 0 or index >= len(dungeons):
        logger.error("Invalid dungeon index: %d", index, extra={"category": "errors"})
        return

    current_dungeon = Dungeon(**DUNGEON_PARAMS)
    current_dungeon.load_state(dungeons[index])

    if current_dungeon is None:
        logger.error("Failed to load dungeon at index %d", index, extra={"category": "errors"})


def place_player_on_staircase(player, dungeon, renderer, use_staircase_up=True):
    """
    Positioniert den Spieler auf einer Treppe (hoch oder runter).
    Fallback: Start-Raum, falls keine Treppe vorhanden.
    """
    if dungeon is None:
        logger.error("Cannot place player: Dungeon is None!", extra={"category": "errors"})
        return

    staircase = dungeon.get_staircase_up() if use_staircase_up else dungeon.get_staircase_down()
    
    if staircase:
        player.x = staircase[0] * renderer.tile_size
        player.y = staircase[1] * renderer.tile_size
        logger.info("Player placed at staircase: (%d, %d)", player.x, player.y, extra={"category": "player"})
    else:
        # Fallback: Start-Raum
        start_room = dungeon.get_start_room()
        if start_room:
            player_x, player_y = start_room.center()
            player.x, player.y = player_x * renderer.tile_size, player_y * renderer.tile_size
            logger.warning("No staircase found. Player placed in start room instead.", extra={"category": "player"})


def go_to_next_level(player, renderer, camera):
    """
    Wechsel zur nächsten Dungeon-Ebene.
    Falls notwendig: neue Ebene generieren und Spieler auf Treppe platzieren.
    """
    global current_level_index, current_dungeon

    if current_dungeon is None:
        logger.error("Cannot go to next level: current_dungeon is None!", extra={"category": "errors"})
        return camera  # Rückgabe der aktuellen Kamera, falls nichts passiert

    # Speichern des aktuellen Dungeon-Zustands
    save_current_dungeon()

    # Neue Ebene generieren, wenn sie noch nicht existiert
    if current_level_index + 1 >= len(dungeons):
        staircase_up_position = current_dungeon.get_staircase_up()
        if staircase_up_position is None:
            logger.error("No staircase found! Cannot generate next level.", extra={"category": "errors"})
            return camera

        new_dungeon = Dungeon(**DUNGEON_PARAMS)
        new_dungeon.generate_next_level(staircase_up_position)
        dungeons.append(new_dungeon.save_state())

    # Erhöht Levelzahl und lade neues Dungeon
    current_level_index += 1
    load_dungeon(current_level_index)

    if current_dungeon is None:
        logger.error("Error: Loaded dungeon is None!", extra={"category": "errors"})
        return camera

    # Kamera neu initialisieren für die neue Ebene
    camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

    logger.info("Moved to next level: %d", current_level_index + 1, extra={"category": "summary"})

    # Spieler auf Treppe platzieren
    place_player_on_staircase(player, current_dungeon, renderer, use_staircase_up=False)

    # **Kamera auf den Spieler zentrieren**
    camera.center_on(player.x, player.y, len(current_dungeon.get_dungeon()), renderer.tile_size)

    return camera  # Neue Kamera zurückgeben


def go_to_previous_level(player, renderer, camera):
    """Wechselt zur vorherigen Dungeon-Ebene, wenn vorhanden."""
    global current_level_index, current_dungeon

    if current_level_index > 0:
        save_current_dungeon()

        current_level_index -= 1
        load_dungeon(current_level_index)

        if current_dungeon is None:
            logger.error("Error: Loaded dungeon is None!", extra={"category": "errors"})
            return camera

        # Spieler auf der Treppe nach oben platzieren
        place_player_on_staircase(player, current_dungeon, renderer, use_staircase_up=True)

        # Kamera neu initialisieren und zentrieren
        camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        camera.center_on(player.x, player.y, len(current_dungeon.get_dungeon()), renderer.tile_size)

        logger.info("Moved to previous level: %d", current_level_index + 1, extra={"category": "summary"})

    return camera


def render_game(screen, dungeon, player, renderer, camera):
    """Rendert Dungeon, Spieler, UI und Minimap."""
    char_slots = {}
    
    # Kamera auf Spieler zentrieren
    camera.center_on(
        player.x,
        player.y,
        len(dungeon.get_dungeon()),  # Anzahl der Zeilen im Dungeon als Höhe der Karte
        renderer.tile_size 
    )
    camera_offset_x, camera_offset_y = camera.offset_x, camera.offset_y

    # Hintergrund löschen & Dungeon rendern
    screen.fill((0, 0, 0))
    renderer.render(screen, dungeon.get_dungeon(), camera_offset_x, camera_offset_y)
    renderer.draw_player(screen, player.x, player.y, player.size, camera_offset_x, camera_offset_y)

    # Minimap zeichnen
    minimap_x = SCREEN_WIDTH - MINIMAP_SIZE[0] - 20
    minimap_y = 20
    draw_minimap(screen, dungeon.get_dungeon(), player.x, player.y, MINIMAP_SIZE)

    # Aktuelle Ebene anzeigen (z. B. „Level 2/5“)
    font = pygame.font.Font(None, 18)
    level_text = f"Level {current_level_index + 1}/{max(1, len(dungeons))}"
    text_surface = font.render(level_text, True, (255, 255, 255))
    screen.blit(text_surface, (minimap_x, minimap_y + MINIMAP_SIZE[1] + 8))

    # Charakter-UI zeichnen
    draw_character_ui(screen, player)

    # Inventar-UI zeichnen, falls geöffnet
    if inventory_open:
        logger.debug("Inventory is open. Drawing inventory UI...", extra={"category": "ui"})
        slot_size = 50
        char_area_y = 100
        char_area_height = 200

        # Inventar- und Charakterwerte zeichnen
        char_slots = draw_inventory_ui(
            screen,
            stats_visible,
            player.stats,
            char_slots,  # Übergibt bestehende Slots oder ein leeres Dict
            char_area_y,
            char_area_height,
            slot_size
        )

    # Skillbar zeichnen (aktuell nur Platzhalter / in Arbeit)
    draw_skillbar(screen, player.skills, player.skill_cooldowns)

    # 🔁 Anzeige aktualisieren
    pygame.display.flip()


def handle_input(player, dungeon, renderer, camera, delta_time, events):
    """
    Verarbeitet Tasteneingaben und Spielerbewegung.
    Rückgabe: ggf. aktualisierte Kamera (z. B. bei Ebenenwechsel).
    """
    global inventory_open, f_key_pressed, last_f_press_time, last_stair_use_time

    keys = pygame.key.get_pressed()
    current_time = time.time()  # Zeitstempel für Entprellung

    # Bewegung nur möglich, wenn das Inventar nicht geöffnet ist
    if not inventory_open:
        move_x = (keys[pygame.K_d] - keys[pygame.K_a]) * player.speed * delta_time
        move_y = (keys[pygame.K_s] - keys[pygame.K_w]) * player.speed * delta_time

        if move_x != 0 or move_y != 0:
            player.move(move_x, move_y, dungeon.get_dungeon(), renderer.tile_size)
            logger.debug(f"Player moved: dx={move_x}, dy={move_y}", extra={"category": "movement"})

    # Weitere Tasteneingaben (Events)
    for event in events:
        if event.type == pygame.KEYDOWN:
            logger.debug(f"Key pressed: {pygame.key.name(event.key)}", extra={"category": "input"})

            # Treppen benutzen mit Taste E (entprellt)
            if not inventory_open and event.key == pygame.K_e:
                if current_time - last_stair_use_time > stair_debounce_time:
                    player_x, player_y = player.x // renderer.tile_size, player.y // renderer.tile_size
                    staircase_up = dungeon.get_staircase_up()
                    staircase_down = dungeon.get_staircase_down()

                    if staircase_up and (player_x, player_y) == staircase_up:
                        logger.info("Interacting with staircase up...", extra={"category": "stairs"})
                        camera = go_to_next_level(player, renderer, camera)

                    elif staircase_down and (player_x, player_y) == staircase_down:
                        logger.info("Interacting with staircase down...", extra={"category": "stairs"})
                        camera = go_to_previous_level(player, renderer, camera)

                    last_stair_use_time = current_time  # Entprellung für Treppen
                else:
                    logger.debug("Stair interaction ignored due to debounce timing", extra={"category": "input"})

            # Inventar öffnen/schließen mit Taste B (entprellt)
            if event.key == pygame.K_b:
                if current_time - last_f_press_time > debounce_duration:
                    inventory_open = not inventory_open  # Status umschalten
                    last_f_press_time = current_time
                    logger.info(f"Inventory {'opened' if inventory_open else 'closed'}.", extra={"category": "ui"})
                else:
                    logger.debug(f"B key debounce active. Time since last press: {current_time - last_f_press_time:.3f}s",
                                 extra={"category": "debug"})

            # Kampffertigkeiten (1–5) mit Cooldown-Check
            if not inventory_open:
                skill_keys = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3, pygame.K_5: 4}

                if event.key in skill_keys:
                    skill_index = skill_keys[event.key]

                    if skill_index < len(player.skills):  # Existiert der Skill?
                        if player.skill_cooldowns[skill_index] <= 0:  # Ist er einsatzbereit?
                            success = player.use_skill(skill_index)
                            if success:
                                logger.info(f"Skill {skill_index + 1} used!", extra={"category": "skills"})
                            else:
                                logger.warning(f"Skill {skill_index + 1} failed (not enough resources?)", extra={"category": "skills"})
                        else:
                            logger.debug(f"Skill {skill_index + 1} is on cooldown ({player.skill_cooldowns[skill_index]:.1f}s left)", extra={"category": "skills"})
                    else:
                        logger.warning(f"Invalid skill index: {skill_index}", extra={"category": "skills"})

            # Debug-Tasten: Schaden nehmen / heilen
            if not inventory_open:
                if event.key == pygame.K_h:  # Schaden nehmen
                    player.take_damage(10)
                    logger.debug("Player took 10 damage.", extra={"category": "debug"})
                elif event.key == pygame.K_j:  # Heilen
                    player.heal(10)
                    logger.debug("Player healed 10 health points.", extra={"category": "debug"})

        # Entprellung für B-Taste beim Loslassen
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_b:
                f_key_pressed = False
                logger.debug("f_key_pressed reset to False.", extra={"category": "input"})

    logger.debug(f"Final Inventory open state: {inventory_open}", extra={"category": "state"})


def main():
    global current_dungeon
    global stats_visible
    global game_state

    # Initialisiere das Spiel und die Komponenten
    logger.debug("Initializing game components...", extra={"category": "init"})
    screen, clock, dungeon, player, renderer, camera = initialize_game()

    current_dungeon = dungeon  # Speichert das initialisierte Dungeon

    # Debug-Ausgabe der Treppenpositionen
    logger.debug("Printing staircase positions...", extra={"category": "stairs"})
    print_staircase_positions(current_dungeon.get_staircase_up(), current_dungeon.get_staircase_down())

    running = True
    while running:
        if game_state == "menu":
            menu.draw()
            selection = menu.handle_input()
            if selection == "Spiel starten":
                game_state = "playing"  # ❌ Kein erneutes `initialize_game()`!
            elif selection == "Spiel beenden":
                running = False

        elif game_state == "playing":
            delta_time = clock.tick(FPS) / 1000.0
            logger.debug("Frame time (delta_time): %.4f seconds", delta_time, extra={"category": "timing"})

            events = pygame.event.get()  # ❗ Nur einmal Events holen!

            for event in events:
                if event.type == pygame.QUIT:
                    logger.info("Quit event detected. Exiting game.", extra={"category": "quit"})
                    running = False
                elif event.type == pygame.KEYDOWN:
                    logger.debug("Key press detected: %s", pygame.key.name(event.key), extra={"category": "input"})
                    if event.key == pygame.K_ESCAPE:
                        game_state = "menu"
                    elif event.key == pygame.K_n:
                        go_to_next_level(player, renderer, camera) 
                    elif event.key == pygame.K_p:
                        go_to_previous_level(player, renderer, camera)

            logger.debug(f"Events existiert? {events is not None} | Typ: {type(events)}", extra={"category": "debug"})
            handle_input(player, current_dungeon, renderer, camera, delta_time, events)  # ✅ Korrekt!

            # FPS in Titelzeile anzeigen
            current_fps = clock.get_fps()
            pygame.display.set_caption(f"Dungeon Crawler - FPS: {int(current_fps)}")

            if current_dungeon is None:
                logger.error("Rendering stopped: current_dungeon is None!", extra={"category": "errors"})
                break

            logger.debug("Rendering game...", extra={"category": "rendering"})
            render_game(screen, current_dungeon, player, renderer, camera)

    pygame.quit()
    logger.info("Game exited successfully.", extra={"category": "quit"})



if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception("An error occurred: %s", e, extra={"category": "errors"})
