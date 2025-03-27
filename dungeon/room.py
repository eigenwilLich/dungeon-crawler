class Room:
    def __init__(self, x, y, width, height):
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive.")
        if x < 0 or y < 0:
            raise ValueError("Coordinates x and y must be non-negative.")

        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def center(self):
        """Gibt die zentrale Position des Raums zurück."""
        return self.x + self.width // 2, self.y + self.height // 2

    def area(self):
        """Berechnet die Fläche des Raums."""
        return self.width * self.height

    def corners(self):
        """Gibt die Eckpunkte des Raums zurück."""
        return [
            (self.x, self.y),  # Oben links
            (self.x + self.width, self.y),  # Oben rechts
            (self.x, self.y + self.height),  # Unten links
            (self.x + self.width, self.y + self.height)  # Unten rechts
        ]

    def intersects(self, other):
        """Überprüft, ob sich dieser Raum mit einem anderen Raum überschneidet."""
        return not self.is_disjoint(other)

    def is_disjoint(self, other):
        """Prüft, ob zwei Räume keine gemeinsame Fläche haben."""
        return (
            self.x + self.width <= other.x or
            self.x >= other.x + other.width or
            self.y + self.height <= other.y or
            self.y >= other.y + other.height
        )

    def __eq__(self, other):
        """Vergleicht Räume basierend auf ihren Positionen und Dimensionen."""
        return (
            self.x == other.x and
            self.y == other.y and
            self.width == other.width and
            self.height == other.height
        )

    def __lt__(self, other):
        """Vergleicht Räume basierend auf ihrer Fläche."""
        return self.area() < other.area()

    def __repr__(self):
        return f"Room(x={self.x}, y={self.y}, width={self.width}, height={self.height})"
    
    def get_bounds(self):
        """
        Gibt die Grenzen des Raums zurück: (x_min, x_max, y_min, y_max).
        """
        x_min = self.x
        y_min = self.y
        x_max = self.x + self.width - 1
        y_max = self.y + self.height - 1
        return x_min, x_max, y_min, y_max

    def contains_point(self, x, y):
        """
        Prüft, ob ein Punkt (x, y) innerhalb des Raums liegt.
        """
        x_min, x_max, y_min, y_max = self.get_bounds()
        return x_min <= x <= x_max and y_min <= y <= y_max
    
    def contains(self, x, y):
        """Prüft, ob die Koordinaten (x, y) innerhalb des Raums liegen."""
        return self.x <= x < self.x + self.width and self.y <= y < self.y + self.height


