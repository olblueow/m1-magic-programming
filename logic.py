import json
import os

class ProgramLoader:
    def __init__(self, json_path):
        """Initializes the loader with the JSON file path."""
        self.json_path = json_path
        self.data = self._load_json()
        
        # Internal state extracted from JSON
        self.tape = self.data.get("initial_tape_state", [])
        self.head_position = self.data.get("initial_head_position", 0)
        self.instructions = self.data.get("instructions", [])
        self.current_step = 0

    def _load_json(self):
        """Reads the JSON file from the disk."""
        if not os.path.exists(self.json_path):
            raise FileNotFoundError(f"The file {self.json_path} was not found.")
        
        with open(self.json_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_next_instruction(self):
        """
        Returns the next instruction to execute.
        Returns None if there are no more instructions.
        """
        if self.current_step < len(self.instructions):
            instr = self.instructions[self.current_step]
            self.current_step += 1
            return instr
        return None

# --- Test Block ---
if __name__ == "__main__":
    # This code only runs if logic.py is executed directly
    try:
        loader = ProgramLoader("data/test_increment.json")
        print(f"Tape loaded: {loader.tape}")
        print(f"Head position: {loader.head_position}")
        
        next_i = loader.get_next_instruction()
        if next_i:
            print(f"First step: {next_i['description']}")
    except Exception as e:
        print(f"Error during testing: {e}")