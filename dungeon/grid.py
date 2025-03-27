class Grid:
    def __init__(self, width, height):
        """Initialisiere ein Raster mit den angegebenen Dimensionen."""
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]

    def is_space_free(self, x, y, room_width, room_height):
        """Prüfe, ob ein Raum mit (room_width x room_height) bei (x, y) platziert werden kann."""
        if x + room_width > self.width or y + room_height > self.height:
            return False

        for i in range(y, y + room_height):
            for j in range(x, x + room_width):
                if self.grid[i][j] == 1:
                    return False
        return True

    def place_room(self, x, y, room_width, room_height):
        """Platziere einen Raum im Raster, wenn genügend Platz vorhanden ist."""
        if not self.is_space_free(x, y, room_width, room_height):
            raise ValueError("Nicht genügend Platz für den Raum!")

        for i in range(y, y + room_height):
            for j in range(x, x + room_width):
                self.grid[i][j] = 1

    def is_cell_occupied(self, x, y):
        """Überprüft, ob die Zelle (x, y) belegt ist."""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x] == 1
        raise ValueError(f"Position ({x}, {y}) liegt außerhalb des Rasters.")
