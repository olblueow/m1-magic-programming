import xml.etree.ElementTree as ET
import os

class ProgramLoader:
    """
    Reads a .cod (XML) deck file and translates it into a list of machine instructions.
    Role 3 responsibility:
    - Parse cards from XML
    - Extract structured parameters (target, etc.)
    - Provide clean data for engine execution
    """
    def __init__(self, cod_path):
        self.cod_path = cod_path
        self.instructions = []
        self.program_name = "Unknown"
        self._load_cod()

    # Annotation Parsing (Role 3)
    def _parse_annotation(self, annotation: str) -> dict:
        """
        Extract structured parameters from annotation string.
        Example:
            "target=2" -> {"target": 2}
        """
        params = {}

        if not annotation:
            return params

        annotation = annotation.lower()

        # target parsing
        if "target=" in annotation:
            try:
                value = annotation.split("target=")[1]
                value = value.split()[0]  # safety (in case of extra text)
                params["target"] = int(value)
            except:
                pass

        #  simple keyword detection (future-proofing)
        if "left" in annotation:
            params["direction"] = "LEFT"
        elif "right" in annotation:
            params["direction"] = "RIGHT"

        return params

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
        if zone is None:
            return
        for card in zone.findall("card"):
             card_name = card.get("name", "Unknown")
             annotation = card.get("annotation", "")

             #  structured parsing (Role 3)
             params = self._parse_annotation(annotation)

             self.instructions.append({
                 "card": card_name,
                 "action": card_action_map.get(card_name, "UNKNOWN"),

                 # (Role 3)
                 "params": params,

                 # keep original for compatibility/debug
                 "annotation": annotation
                })