import random
import logging
from .room import Room
from .corridor import Corridor
from .tile import TileType
from heapq import heappop, heappush
from utils.logger_config import logger
from dungeon.grid import Grid
from utils.config import TILE_SIZE


logger = logging.getLogger("DungeonGame")


class Dungeon:
    def __init__(self, width, height, min_rooms, max_rooms, room_size_range, seed=None, debug=False, grid=None):
        if seed is not None:
            random.seed(seed)  # Seed für die Zufallszahlengenerierung setzen
            self.debug_print(f"Random seed set to {seed}")

        self.width = width
        self.height = height
        self.min_rooms = min_rooms
        self.max_rooms = max_rooms
        self.room_size_range = room_size_range

        # 2D-Array zur Darstellung des Dungeons (initial: nur Wände)
        self.dungeon = [[TileType.WALL for _ in range(width)] for _ in range(height)]

        # Liste aller generierten Räume
        self.rooms = []

        # Positionen von Treppen
        self.staircase_up = None
        self.staircase_down = None

        # Bereits verbundene Korridore
        self.existing_corridors = set() 

        # Startraum-Referenz
        self.start_room = None

        self.generated = False  # Verhindert doppelte Generierung
        self.debug = debug
        self.grid = grid if grid else Grid(width, height)  # Grid verwenden oder erstellen

    def log_grid(self):
        """Gibt das aktuelle Dungeon-Grid zeilenweise ins Log aus (nur zu Debugzwecken)."""
        logger.info("Dungeon Grid State:", extra={"category": "grid"})
        for y, row in enumerate(self.dungeon):
            logger.info("".join(str(tile) for tile in row), extra={"category": "grid"})
        logger.info("Dungeon grid output completed.", extra={"category": "grid"})

    def set_grid(self, grid):
        """Erlaubt das Setzen eines externen Grids."""
        self.grid = grid

    def generate(self, start_level=False):
        """
        Generiert das Dungeon: Räume erstellen, Korridore verbinden, Treppen setzen.
        Bei start_level=True wird nur die Treppe nach oben erstellt.
        """
        if self.generated:
            logger.warning("Dungeon generation already completed. Skipping.", extra={"category": "levels"})
            return

        self.generated = True
        logger.info("Generating dungeon...", extra={"category": "summary"})

        num_rooms = random.randint(self.min_rooms, self.max_rooms)
        attempts = 0

        # Räume generieren, bis Mindestanzahl erreicht oder max. Versuche überschritten
        while len(self.rooms) < num_rooms and attempts < num_rooms * 5:
            room = self._create_random_room()
            if not self._rooms_overlap_or_touch(room, self.rooms):  # Hier wird die Methode aufgerufen
                self.rooms.append(room)
                self._carve_room(room)
                logger.debug("Room created: %s", room, extra={"category": "rooms"})
            attempts += 1

        if not self.rooms:
            logger.error("No rooms generated. Dungeon generation failed.", extra={"category": "levels"})
            raise ValueError("No rooms generated. Dungeon generation failed.")

        # Räume verbinden
        self._connect_rooms()

        # Start-Raum auswählen (für Spielerstart, nur 1× pro Dungeon)
        self._select_start_room()

        logger.info("Rooms created: %d", len(self.rooms), extra={"category": "rooms"})
        for i, room in enumerate(self.rooms):
            logger.debug("Room %d: %s at %s", i, room, room.center(), extra={"category": "rooms"})

        if start_level:
            # Nur eine Treppe im Start-Level, entfernt vom Start-Raum
            if not self.start_room:
                logger.error("Start room not defined.", extra={"category": "levels"})
                raise ValueError("Start room not defined.")
            logger.info("Start room selected: %s", self.start_room, extra={"category": "rooms"})
            distant_room = random.choice([room for room in self.rooms if room != self.start_room])
            self.staircase_up = self._place_staircase(distant_room, TileType.STAIRS_UP)
            logger.info("Staircase Up placed in room: %s at %s", distant_room, self.staircase_up, extra={"category": "stairs"})
            self.staircase_down = None  # Keine Treppe nach unten im Start-Level
        else:
            # Normale Ebenen bekommen beide Treppen (z. B. Ebene 2, 3, ...)
            self.staircase_up = self._place_staircase(self.rooms[0], TileType.STAIRS_UP)
            self.staircase_down = self._place_staircase(self.rooms[-1], TileType.STAIRS_DOWN)

        logger.debug("Generating room: %s", room, extra={"category": "rooms"})
        logger.debug("Room overlaps or touches another room: %s", room, extra={"category": "rooms"})

        self.debug_stairs()

    def generate_next_level(self, staircase_down_position):
        """
        Generiert eine neue Dungeon-Ebene mit Übergang von der vorherigen.
        Die übergebene staircase_down_position ist der Einstiegspunkt in die neue Ebene.
        """
        logger.info("Generating next level with staircase_down at %s", staircase_down_position, extra={"category": "levels"})
        self.rooms = [] # Räume zurücksetzen
        self.dungeon = [[TileType.WALL for _ in range(self.width)] for _ in range(self.height)]

        # 1. Tile an der Treppenposition begehbar machen
        x_down, y_down = staircase_down_position
        if not 0 <= x_down < self.width or not 0 <= y_down < self.height:
            logger.error("Staircase Down position %s is out of bounds.", staircase_down_position, extra={"category": "stairs"})
            raise ValueError(f"Staircase Down position {staircase_down_position} is out of bounds.")
        self.dungeon[y_down][x_down] = TileType.FLOOR
        logger.info("Marked staircase_down position %s as walkable (FLOOR).", staircase_down_position, extra={"category": "stairs"})

        # 2. Treppe nach unten auf dem begehbaren Tile platzieren
        self.dungeon[y_down][x_down] = TileType.STAIRS_DOWN
        self.staircase_down = staircase_down_position
        logger.info("Placed staircase_down at %s.", staircase_down_position, extra={"category": "summary"})

        # 3. Raum um die Treppe bauen
        staircase_room = self._create_room_around_point(x_down, y_down)
        self.rooms.append(staircase_room)
        self._carve_room(staircase_room, force=True)
        logger.info("Created room around staircase_down at %s.", staircase_down_position, extra={"category": "rooms"})

        # 4. Weitere Räume hinzufügen (außer dem für die Treppe)
        num_rooms = random.randint(self.min_rooms, self.max_rooms)
        logger.debug("Generating %d additional rooms for the level.", num_rooms - 1, extra={"category": "levels"})
        attempts = 0

        while len(self.rooms) < num_rooms and attempts < num_rooms * 5:
            room = self._create_random_room()
            if not self._rooms_overlap_or_touch(room, self.rooms):
                self.rooms.append(room)
                self._carve_room(room)
                logger.debug("Room created: %s", room, extra={"category": "rooms"})
            attempts += 1

        # Räume verbinden
        self._connect_rooms()

        # Validierung: Sicherstellen, dass STAIRS_DOWN nicht überschrieben wurde
        if self.dungeon[y_down][x_down] != TileType.STAIRS_DOWN:
            logger.error("STAIRS_DOWN at (%d, %d) was overwritten. Restoring...", x_down, y_down, extra={"category": "stairs"})
            self.dungeon[y_down][x_down] = TileType.STAIRS_DOWN

        # 5. Treppe nach oben in einem zufälligen Raum platzieren
        distant_room = random.choice([room for room in self.rooms if room != staircase_room])
        staircase_up_position = distant_room.center()
        x_up, y_up = staircase_up_position

        # Sicherstellen, dass das Tile begehbar ist
        if not self.is_walkable_tile(x_up, y_up):
            logger.warning(
                "Staircase Up position %s is not walkable. Adjusting position...",
                staircase_up_position, extra={"category": "stairs"}
            )
            staircase_up_position = self._find_walkable_position_in_room(distant_room)
            if not staircase_up_position:
                logger.error(
                    "No valid walkable position found in room %s for Staircase Up.",
                    distant_room, extra={"category": "stairs"}
                )
                raise ValueError("No valid walkable position found for Staircase Up.")

        # Treppe nach oben platzieren
        self.dungeon[y_up][x_up] = TileType.STAIRS_UP
        self.staircase_up = staircase_up_position
        logger.info("Placed staircase_up at %s in room %s.", staircase_up_position, distant_room, extra={"category": "summary"})

        # Debugging der Treppen
        self.debug_stairs()

    def _create_room_around_point(self, x, y):
        """Erstellt einen Raum zufälliger Größe um einen gegebenen Mittelpunkt (z. B. für Treppenplatzierung)."""
        max_attempts = 10
        buffer = 1  # Abstand zwischen Räumen

        # Zufällige Raumgröße
        for attempt in range(max_attempts):
            # Zufällige Raumgröße innerhalb des Bereichs
            room_width = random.randint(self.room_size_range[0], self.room_size_range[1])
            room_height = random.randint(self.room_size_range[0], self.room_size_range[1])

            # Zentriere Raum um den Punkt, mit minimalem Abstand zum Rand
            room_x = max(1, x - room_width // 2)
            room_y = max(1, y - room_height // 2)

            # Stelle sicher, dass der Raum nicht über den Dungeon hinausgeht
            room_width = min(room_width, self.width - room_x - 1)
            room_height = min(room_height, self.height - room_y - 1)

            new_room = Room(room_x, room_y, room_width, room_height)

            # Prüfen auf Kollision mit bestehenden Räumen
            if not self._rooms_overlap_or_touch(new_room, self.rooms, buffer=buffer):
                logger.info(
                    "Random-sized room created around point (%d, %d) after %d attempts: %s",
                    x, y, attempt + 1, new_room, extra={"category": "rooms"}
                )
                return new_room

            # Versatz für nächsten Versuch
            logger.debug(
                "Failed to place room at (%d, %d) on attempt %d. Adjusting parameters...",
                room_x, room_y, attempt + 1, extra={"category": "rooms"}
            )
            x = (x + random.randint(-1, 1)) % self.width
            y = (y + random.randint(-1, 1)) % self.height

        # Fallback – wenn alle Versuche fehlschlagen, erstelle einen kleinen Raum
        logger.warning(
            "Forced room placement around point (%d, %d) after %d attempts.",
            x, y, max_attempts, extra={"category": "rooms"}
        )
        return Room(max(1, x - 1), max(1, y - 1), 3, 3)

    def _rooms_overlap_or_touch(self, room, other_rooms, buffer=1):
        """
        Prüft, ob sich ein Raum mit anderen Räumen überschneidet oder direkt angrenzt.
        buffer=1 erlaubt 1 Feld Abstand.
        """
        for y in range(room.y - buffer, room.y + room.height + buffer):
            for x in range(room.x - buffer, room.x + room.width + buffer):
                if 0 <= x < self.width and 0 <= y < self.height:
                    if self.grid.is_cell_occupied(x, y):
                        logger.debug("Room %s overlaps or touches another room at (%d, %d).", room, x, y, extra={"category": "rooms"})
                        return True
        logger.debug("Room %s does not overlap with any existing room.", room, extra={"category": "rooms"})
        return False

    def _create_random_room(self):
        """Erstellt einen vollständig zufälligen Raum innerhalb der Dungeon-Grenzen."""
        width = random.randint(self.room_size_range[0], self.room_size_range[1])
        height = random.randint(self.room_size_range[0], self.room_size_range[1])
        x = random.randint(1, self.width - width - 2)
        y = random.randint(1, self.height - height - 2)
        room = Room(x, y, width, height)
        logger.debug("Generated random room: %s", room, extra={"category": "rooms"})
        return Room(x, y, width, height)

    def _connect_rooms(self):
        """
        Verbindet alle Räume über ein Minimum Spanning Tree (MST),
        um sicherzustellen, dass jeder Raum erreichbar ist.
        """
        from heapq import heappop, heappush

        edges = []
        for i, room1 in enumerate(self.rooms):
            for j, room2 in enumerate(self.rooms):
                if i < j:
                    dist = abs(room1.center()[0] - room2.center()[0]) + abs(room1.center()[1] - room2.center()[1])
                    heappush(edges, (dist, i, j))

        parent = list(range(len(self.rooms)))

        def find(v):
            if parent[v] != v:
                parent[v] = find(parent[v])
            return parent[v]

        def union(v1, v2):
            parent[find(v2)] = find(v1)

        mst = []
        while edges and len(mst) < len(self.rooms) - 1:
            dist, i, j = heappop(edges)
            if find(i) != find(j):
                union(i, j)
                mst.append((i, j))

        for i, j in mst:
            logger.info("Connected room %d to room %d.", i, j, extra={"category": "corridors"})
            Corridor.create(self.dungeon, self.rooms[i].center(), self.rooms[j].center())

        # Überprüfen, ob alle Räume verbunden sind
        connected = set(find(i) for i in range(len(self.rooms)))
        if len(connected) > 1:
            logger.error("Some rooms are still isolated after connecting.", extra={"category": "corridors"})
            raise ValueError("Some rooms are still isolated after connecting.")

    def _select_start_room(self):
        """
        Wählt einen Raum mit nur einer Verbindung als Startpunkt (wenn möglich).
        Fallback: erster Raum in der Liste.
        """
        for room in self.rooms:
            connections = sum(1 for other in self.rooms if self._corridor_exists(room.center(), other.center()))
            logger.debug("Room %s at %s has %d connections.", room, room.center(), connections, extra={"category": "rooms"})
            if connections == 1:  # Startraum hat nur eine Verbindung
                self.start_room = room
                logger.info("Start room selected: %s", room, extra={"category": "rooms"})
                return

        # Fallback: Wähle den ersten Raum, falls kein passender gefunden wird
        if self.rooms:  # Sicherstellen, dass es mindestens einen Raum gibt
            logger.warning("No suitable start room with one connection found. Selecting the first room as fallback.", extra={"category": "rooms"})
            self.start_room = self.rooms[0]
        else:
            logger.error("No rooms available to select a start room.", extra={"category": "rooms"})
            raise ValueError("No rooms available to select a start room.")
        
    def _carve_room(self, room, force=False):
        logger.debug("Carving room: %s (force=%s)", room, force, extra={"category": "rooms"})
        if not force and not self.grid.is_space_free(room.x, room.y, room.width, room.height):
            raise ValueError(f"Nicht genügend Platz für den Raum {room}!")

        self.grid.place_room(room.x, room.y, room.width, room.height)
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                # Überspringen, wenn die Position STAIRS_DOWN ist
                if self.dungeon[y][x] == TileType.STAIRS_DOWN:
                    logger.warning("Skipping carving at (%d, %d) to avoid overwriting STAIRS_DOWN.", x, y, extra={"category": "rooms"})
                    continue
                self.dungeon[y][x] = TileType.FLOOR

        logger.debug("Finished carving room: %s", room, extra={"category": "rooms"})

    def _corridor_exists(self, start, end):
        """Prüft, ob ein Korridor zwischen zwei Punkten existiert."""
        return (start, end) in self.existing_corridors or (end, start) in self.existing_corridors 

    def get_start_room(self):
        """Gibt den Startraum zurück."""
        return self.start_room

    def debug_stairs(self):
        """Validiert die Position und Korrektheit der Treppen."""
        stairs_up_count = sum(row.count(TileType.STAIRS_UP) for row in self.dungeon)
        stairs_down_count = sum(row.count(TileType.STAIRS_DOWN) for row in self.dungeon)
        logger.info("STAIRS_UP count: %d", stairs_up_count, extra={"category": "summary"})
        logger.info("STAIRS_DOWN count: %d", stairs_down_count, extra={"category": "summary"})

        if self.staircase_down:
            x, y = self.staircase_down
            if self.dungeon[y][x] != TileType.STAIRS_DOWN:
                logger.error("STAIRS_DOWN at (%d, %d) is missing or incorrect.", x, y, extra={"category": "stairs"})
            elif not self.is_walkable_tile(x, y):
                logger.error("STAIRS_DOWN at (%d, %d) is not walkable.", x, y, extra={"category": "stairs"})
            else:
                logger.info("STAIRS_DOWN at (%d, %d) is walkable and correct.", x, y, extra={"category": "stairs"})

    def _place_staircase(self, room, tile_type):
        """Setzt eine Treppe im Zentrum oder an einem begehbaren Tile im Raum."""
        center = room.center()
        x, y = center

        if not self.is_walkable_tile(x, y):
            logger.warning(
                "Cannot place %s at %s (not walkable). Searching alternative position...",
                tile_type, center, extra={"category": "stairs"}
            )
            walkable_position = self._find_walkable_position_in_room(room)
            if not walkable_position:
                logger.error("No walkable position found in room %s for %s.", room, tile_type, extra={"category": "stairs"})
                raise ValueError(f"No walkable position found in room {room} for {tile_type}.")
            x, y = walkable_position

        self.dungeon[y][x] = tile_type
        logger.info("Placed staircase (%s) at %s.", tile_type, (x, y), extra={"category": "stairs"})

        # Validierung hinzufügen
        if self.dungeon[y][x] != tile_type:
            logger.error("Failed to place staircase (%s) at %s. Tile is %s.", tile_type, (x, y), self.dungeon[y][x])
            raise ValueError(f"Failed to place staircase at {x}, {y}.")
        return (x, y)

    def get_staircase_up(self):
        """Gibt die Position der Treppe nach oben zurück."""
        return self.staircase_up

    def get_staircase_down(self):
        """Gibt die Position der Treppe nach unten zurück."""
        return self.staircase_down
    
    def get_dungeon(self):
        """Gibt die Dungeon-Datenstruktur zurück."""
        return self.dungeon
    
    def save_state(self):
        """Speichert den aktuellen Zustand des Dungeons (für Levelwechsel)."""
        return {
            "dungeon": self.dungeon,
            "rooms": self.rooms,
            "staircase_up": self.staircase_up,
            "staircase_down": self.staircase_down,
            "start_room": self.start_room,
            # Ergänze weitere Attribute wie Gegner oder Gegenstände hier
        }

    def load_state(self, state):
        """Lädt einen gespeicherten Dungeon-Zustand."""
        self.dungeon = state["dungeon"]
        self.rooms = state["rooms"]
        self.staircase_up = state["staircase_up"]
        self.staircase_down = state["staircase_down"]
        self.start_room = state["start_room"]
        

    def is_walkable_tile(self, x, y):
        """Überprüft, ob das Tile an der gegebenen Position begehbar ist."""
        if 0 <= x < self.width and 0 <= y < self.height:
            tile = self.dungeon[y][x]
            walkable = tile in [TileType.FLOOR, TileType.STAIRS_UP, TileType.STAIRS_DOWN]
            logger.debug(
                "Tile at (%d, %d) is %s", x, y,
                "walkable" if walkable else "not walkable",
                extra={"category": "tiles"}
            )
            return walkable
        logger.debug("Tile at (%d, %d) is out of bounds.", x, y, extra={"category": "tiles"})
        return False
    
    def _find_walkable_position_in_room(self, room):
        """Sucht nach einem begehbaren Tile innerhalb eines Raums."""
        for y in range(room.y, room.y + room.height):
            for x in range(room.x, room.x + room.width):
                if self.is_walkable_tile(x, y):
                    logger.debug("Found walkable tile at (%d, %d) in room %s.", x, y, room, extra={"category": "tiles"})
                    return (x, y)
        logger.warning("No walkable tiles found in room %s.", room, extra={"category": "tiles"})
        return None

    def check_for_traps(player, dungeon):
        """Prüft, ob der Spieler auf eine Falle tritt."""
        player_tile = (
            player.x // TILE_SIZE,
            player.y // TILE_SIZE,
        )
        if dungeon.get_tile(player_tile) == TileType.TRAP:
            player.take_damage(15)
            logger.info("Player stepped on a trap!", extra={"category": "gameplay"})




