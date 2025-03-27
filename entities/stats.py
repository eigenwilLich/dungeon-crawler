class Stats:
    def __init__(self):
        self.data = {
                    "Offensiv": {
                        "Stärke": 15,
                        "Geschicklichkeit": 12,
                        "Magiekraft": 10,
                        "Kritischer Schaden": "25%",
                    },
                    "Defensiv": {
                        "Rüstung": 20,
                        "Magieresistenz": 18,
                        "Ausweichen": "5%",
                        "Gesundheit": 120,
                        "Regeneration": "2 HP/sec",
                    },
                    "Ressourcen": {
                        "Mana": 50,
                        "Energie": 100,
                        "Regeneration": "5 Mana/sec",
                        "Ausdauer": 10,
                    },
                    "Unterstützend": {
                        "Glück": "8%",
                        "Erfahrung": "+10%",
                        "Gold-Bonus": "+5%",
                    },
                    "Spezielle Werte": {
                        "Lebensraub": "2%",
                        "Manaraub": "3%",
                        "Schadensreflexion": "1%",
                        "Elementarschaden": "+10% Feuer",
                        "Elementarresistenz": "+15% Blitz",
                    },
                }