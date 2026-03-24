import xml.etree.ElementTree as ET
import os

class ProgramLoader:
    def __init__(self, cod_path):
        """
        Initializes the loader with a .cod (XML) file path.
        The .cod file contains ONLY the deck (the program instructions).
        """
        self.cod_path = cod_path
        self.instructions = []
        self.program_name = "Unknown"
        self._load_cod()
        self.current_step = 0

    def _load_cod(self):
        """Parses the .cod XML file and extracts the list of cards."""
        if not os.path.exists(self.cod_path):
            raise FileNotFoundError(f"The file {self.cod_path} was not found.")

        tree = ET.parse(self.cod_path)
        root = tree.getroot()

        # --- Extract program name ---
        deckname_el = root.find("deckname")
        self.program_name = deckname_el.text.strip() if deckname_el is not None else "Unknown"

        # --- Extract instructions from <zone name="main"> ---
        # Card name → action mapping
        card_action_map = {
            "Artificial Evolution": "CONFIG",
            "Infest":               "EXECUTE",
            "Bioshift":             "MOVE_RIGHT",
            "Fate Transfer":        "MOVE_LEFT",
            "Slime Molding":        "SETUP_CREATE",
            "Battlegrowth":         "SETUP_PROTECT",
        }

        zone = root.find(".//zone[@name='main']")
        if zone is not None:
            for card in zone.findall("card"):
                card_name = card.get("name", "Unknown")
                action = card_action_map.get(card_name, "UNKNOWN")
                annotation = card.get("annotation", "")

                self.instructions.append({
                    "card":        card_name,
                    "action":      action,
                    "annotation":  annotation
                })

    def get_next_instruction(self):
        """Returns the next instruction dict to execute, or None if finished."""
        if self.current_step < len(self.instructions):
            instr = self.instructions[self.current_step]
            self.current_step += 1
            return instr
        return None