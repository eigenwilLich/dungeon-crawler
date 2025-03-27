
# 🧱 Dungeon Crawler

Ein 2D-Dungeon-Crawler-Spiel auf Basis von **Pygame**, mit zufällig generierten Ebenen, einer interaktiven Minimap, einem UI für Inventar und Charakterstatistiken sowie einer modularen Codebasis.

---

## 🕹️ Features

- 🔁 **Prozedurale Dungeon-Generierung** mit Räumen, Korridoren und mehreren Ebenen (Generierung bei Wechsel auf neue Ebene)
- 🧍‍♂️ **Spielercharakter** mit Position, Bewegung, Statuswerten, Inventar und Fertigkeiten
- 🧟‍♂️ **Gegner- und Item-System** zur Erweiterung der Spielwelt (geplant)
- 🗺️ **Kamera- und Minimap-System** für Übersichtlichkeit
- 💡 **UI-Komponenten** für:
      - Lebensbalken & Ausdauer
      - Inventar
      - Skill-Leiste
- 🔧 **Konfigurierbare Parameter** (Dungeon-Größe, Raumanzahl, Seed etc.)
- 📋 **Hauptmenü** und Tastenkürzel zur Steuerung

---

## 🗂️ Projektstruktur

```
Dungeon Crawler/
├── main.py
├── menu.py
├── dungeon/
├── entities/
├── rendering/
├── utils/
└── ...
```

---

## 🚀 Installation & Ausführung

### Voraussetzungen

- Python 3.11 oder höher
- Pygame

### Installation

Öffne dein Terminal (z.B. das integrierte Terminal deiner IDE) und installiere die Abhängigkeiten:

```bash
pip install -r requirements.txt
```

### Spiel starten

```bash
python main.py
```

---

## 🎮 Steuerung

| Taste         | Funktion                                    |
|---------------|---------------------------------------------|
| `↑ ↓ Enter`   | Menüführung                                 |
| `W A S D`     | Bewegung des Spielers                       |
| `1 2 3 4 5`   | Skills (noch nicht implementiert)           |
| `E`           | Interaktion mit Treppen (später auch Truhen)|
| `B`           | Charakter-/Inventaransicht umschalten       |
| `Esc`         | Zurück ins Menü / Spiel verlassen           |

---

## 🧩 Dungeon-Elemente

| Element            | Darstellung / Farbe          | Bedeutung                         |
|--------------------|------------------------------|-----------------------------------|
| Boden (Floor)      | Dunkelgrün                   | Begehbare Fläche                  |
| Wand (Wall)        | Olivgrün                     | Undurchlässig, blockiert Bewegung |
| Treppe nach oben   | Hellgrün 🟩                  | Führt in eine höhere Ebene        |
| Treppe nach unten  | Rot 🟥                       | Führt in eine tiefere Ebene       |
| Spieler            | Weiß                         | Deine aktuelle Position           |

---

## ⚙️ Konfigurierbare Parameter

Die Datei `utils/config.py` enthält zentrale Einstellungen wie:

- Bildschirmgröße (`SCREEN_WIDTH`, `SCREEN_HEIGHT`)
- Dungeon-Parameter (`DUNGEON_PARAMS`)
- Minimapskalierung (`MINIMAP_SIZE`)
- FPS-Begrenzung (`FPS`)

---

## 🛠️ Entwicklungsstand

✅ Bereits implementiert:
- Dungeon-Generierung
- Spielercharakter & Kamera
- Rendering & Minimap
- UI & Menüsystem

🚧 Geplante Features (Beispiele):
- Skill- und Itemsystem
- Kampf- und Kollisionssystem
- Verschiedene Gegnertypen
- Fog of War
- Fortschrittsspeicherung
- KI-gestützte Spielbalance, die sich dynamisch an Spielverhalten anpasst (Schwierigkeit, Itemverteilung etc.)
- Grafische Elemente
- Sound- und Musikunterstützung

---

## 📚 Lizenz

Dieses Projekt steht unter der MIT-Lizenz – siehe `LICENSE`-Datei für Details.

---

## ✍️ Autor

Erstellt von eigenwilLich (Alan Carl).  
Kontaktiere mich bei Fragen oder für Feedback gern über GitHub oder per E-Mail.
