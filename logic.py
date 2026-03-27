import xml.etree.ElementTree as ET
import os

class ProgramLoader:
    """
    Reads a .cod (XML) deck file and translates it into a list of machine instructions.
    """
    def __init__(self, cod_path):
        self.cod_path = cod_path
        self.instructions = []
        self.program_name = "Unknown"
        self._load_cod()

    def _load_cod(self):
        """Parses the XML and maps Magic cards to system actions."""
        if not os.path.exists(self.cod_path):
            raise FileNotFoundError(f"File not found: {self.cod_path}")

        tree = ET.parse(self.cod_path)
        root = tree.getroot()

        # Extract program name
        deckname_el = root.find("deckname")
        if deckname_el is not None:
            self.program_name = deckname_el.text.strip()

        # Instruction Set Architecture (ISA) Mapping
        card_action_map = {
            "Artificial Evolution": "CONFIG",
            "Infest":               "EXECUTE",
            "Bioshift":             "MOVE_RIGHT",
            "Fate Transfer":        "MOVE_LEFT",
            "Slime Molding":        "SETUP_CREATE",
            "Battlegrowth":         "SETUP_PROTECT",
        }

        # Extract cards from the main deck
        zone = root.find(".//zone[@name='main']")
        if zone is not None:
            for card in zone.findall("card"):
                card_name = card.get("name", "Unknown")
                
                self.instructions.append({
                    "card":       card_name,
                    "action":     card_action_map.get(card_name, "UNKNOWN"),
                    "annotation": card.get("annotation", "")
                })