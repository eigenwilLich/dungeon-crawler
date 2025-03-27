import logging

# Logger erstellen
logger = logging.getLogger("DungeonGame")
logger.setLevel(logging.DEBUG)  # Setze das allgemeine Log-Level auf DEBUG

# Debugging aktivieren
ENABLE_ALL_DEBUG = False
ENABLED_CATEGORIES = {"summary", "ui", "movement"}  # Kategorien "summary" und "ui" bleiben aktiv

# Format für Logs
formatter = logging.Formatter("%(asctime)s [%(levelname)s] [%(category)s] %(message)s")

# Summary-Handler: Aktiv für die Kategorie "summary"
summary_handler = logging.StreamHandler()
summary_handler.setLevel(logging.INFO)  # Zeigt nur INFO und höher an
summary_formatter = logging.Formatter("%(asctime)s [SUMMARY] %(message)s")
summary_handler.setFormatter(summary_formatter)

class SummaryFilter(logging.Filter):
    def filter(self, record):
        return getattr(record, "category", None) == "summary"

summary_handler.addFilter(SummaryFilter())
logger.addHandler(summary_handler)

# UI-Handler: Aktiv für Nachrichten der Kategorie "ui"
ui_handler = logging.StreamHandler()
ui_handler.setLevel(logging.INFO)  # Zeigt nur INFO und höher an
ui_formatter = logging.Formatter("%(asctime)s [UI] %(message)s")
ui_handler.setFormatter(ui_formatter)

class UiFilter(logging.Filter):
    def filter(self, record):
        return getattr(record, "category", None) == "ui"

ui_handler.addFilter(UiFilter())
logger.addHandler(ui_handler)

# Debug-Handler: Zeigt alle Debug-Nachrichten an
debug_handler = logging.StreamHandler()
debug_handler.setLevel(logging.DEBUG)  # Zeigt alle Nachrichten ab DEBUG an
debug_formatter = logging.Formatter("%(asctime)s [DEBUG] [%(category)s] %(message)s")
debug_handler.setFormatter(debug_formatter)

# Filter für Debugging: Zeige alles an, wenn ENABLE_ALL_DEBUG True ist
if ENABLE_ALL_DEBUG:
    logger.setLevel(logging.DEBUG)
    logger.addHandler(debug_handler)

# Kategorie-Filter: Allgemeiner Filter für andere Kategorien
class CategoryFilter(logging.Filter):
    def __init__(self, enabled_categories):
        self.enabled_categories = enabled_categories

    def filter(self, record):
        # Standardmäßig die Kategorie auf "general" setzen, falls keine vorhanden ist
        if not hasattr(record, "category"):
            record.category = "general"

        # Wenn Kategorien deaktiviert sind, zeige alles an
        if self.enabled_categories is None:
            return True
        return record.category in self.enabled_categories

# Kategorie-Filter für den Logger hinzufügen, falls aktiviert
if not ENABLE_ALL_DEBUG:
    logger.addFilter(CategoryFilter(ENABLED_CATEGORIES))
