class Camera:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.offset_x = 0
        self.offset_y = 0

    def center_on(self, player_x, player_y, map_height, tile_size):
        """Zentriert die Kamera auf den Spieler."""
        self.offset_x = max(0, player_x - self.screen_width // 2)
        self.offset_y = max(0, player_y - self.screen_height // 2)

        # Begrenzung auf die Kartenränder
        max_x = map_height * tile_size - self.screen_width
        max_y = map_height * tile_size - self.screen_height
        self.offset_x = min(self.offset_x, max_x)
        self.offset_y = min(self.offset_y, max_y)

    def get_screen_position(self, x: int, y: int, tile_size: int) -> tuple[int, int]:
        """
        Konvertiert Kartenkoordinaten in Bildschirmkoordinaten basierend auf dem Kamera-Offset.
        :param x: X-Koordinate auf der Karte in Kacheln.
        :param y: Y-Koordinate auf der Karte in Kacheln.
        :param tile_size: Größe einer Kachel in Pixeln.
        :return: Tupel der Bildschirmkoordinaten (x, y).
        """
        screen_x = x * tile_size - self.offset_x
        screen_y = y * tile_size - self.offset_y
        return screen_x, screen_y
