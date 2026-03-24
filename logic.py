import xml.etree.ElementTree as ET
import os

class ProgramLoader:
    def __init__(self, cod_path):
        """
        Initializes the loader with a .cod (XML) file path.
        The .cod file contains:
          - <deckname>     : program name
          - <comments>     : metadata (initial tape, head position, encoding)
          - <zone name="main"> : sequence of cards = instructions
        """
        self.cod_path = cod_path
        self._load_cod()
        self.current_step = 0

    def _load_cod(self):
        """Parses the .cod XML file and extracts tape, head position, and instructions."""
        if not os.path.exists(self.cod_path):
            raise FileNotFoundError(f"The file {self.cod_path} was not found.")

        tree = ET.parse(self.cod_path)
        root = tree.getroot()

        # --- Extract program name ---
        deckname_el = root.find("deckname")
        self.program_name = deckname_el.text.strip() if deckname_el is not None else "Unknown"

        # --- Extract metadata from <comments> ---
        # Expected format inside <comments>:
        #   TAPE: 0,1,1
        #   HEAD: 0
        self.tape = []
        self.head_position = 0

        comments_el = root.find("comments")
        if comments_el is not None and comments_el.text:
            for line in comments_el.text.splitlines():
                line = line.strip()
                if line.startswith("TAPE:"):
                    values = line.replace("TAPE:", "").strip()
                    self.tape = [int(v.strip()) for v in values.split(",")]
                elif line.startswith("HEAD:"):
                    self.head_position = int(line.replace("HEAD:", "").strip())

        # Default tape if not found in comments
        if not self.tape:
            self.tape = [0]

        # --- Extract instructions from <zone name="main"> ---
        # Each <card> is one instruction.
        # The card's name maps to an action:
        #   "Artificial Evolution" → CONFIG  (reprogram Rotlung, no tape change)
        #   "Infest"               → EXECUTE (kill head token, trigger write)
        #   "Bioshift"             → MOVE_RIGHT
        #   "Fate Transfer"        → MOVE_LEFT
        #
        # Annotations inside the card's XML comments provide description + details.
        self.instructions = []

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

                # Extract annotation if present (optional extra info)
                annotation = card.get("annotation", "")

                self.instructions.append({
                    "card":        card_name,
                    "action":      action,
                    "annotation":  annotation,
                    "description": f"{card_name} → {action}"
                })

    def get_next_instruction(self):
        """
        Returns the next instruction dict to execute, or None if finished.
        Each instruction has:
          - card        : MTG card name (e.g. "Infest")
          - action      : what to do   (e.g. "EXECUTE", "MOVE_RIGHT")
          - annotation  : optional extra info from the .cod
          - description : human-readable summary
        """
        if self.current_step < len(self.instructions):
            instr = self.instructions[self.current_step]
            self.current_step += 1
            return instr
        return None

    def reset(self):
        """Reloads the .cod file from scratch (useful for restart button)."""
        self._load_cod()
        self.current_step = 0


# --- Test Block ---
if __name__ == "__main__":
    try:
        loader = ProgramLoader("data/binary_increment.cod")
        print(f"Program    : {loader.program_name}")
        print(f"Tape       : {loader.tape}")
        print(f"Head pos   : {loader.head_position}")
        print(f"Nb steps   : {len(loader.instructions)}")
        print()

        for i in range(min(5, len(loader.instructions))):
            instr = loader.get_next_instruction()
            print(f"Step {i+1:02d} : [{instr['card']}] → {instr['action']}")
            if instr['annotation']:
                print(f"         annotation: {instr['annotation']}")

    except Exception as e:
        print(f"Error: {e}")