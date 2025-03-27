class Item:
    def __init__(self, x, y, name, effect):
        self.x = x
        self.y = y
        self.name = name
        self.effect = effect

    def apply_effect(self, player):
        """Wendet den Effekt des Items auf den Spieler an."""
        pass  # Implementiere spezifische Effekte