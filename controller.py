from loader import DeckLoader
from battlefield import Battlefield
from engine import GameEngine
import cards.factory as factory
import copy


class GameController:
    """
    Main controller coordinating the execution of a compiled Magic deck.
    Reads instructions, instantiates cards, and passes them to the Game Engine.
    """
    def __init__(self, cod_path: str):
        self.cod_path = cod_path

        # Core components
        self.loader = None
        self.instructions = []

        self.board = None
        self.engine = None

        # State tracking
        self.current_step = 0
        self.history = []
        self.loaded = False

    # ----------
    # Load game
    # ----------
    def load(self):
        """Loads the XML .cod file and initializes the battlefield and engine."""
        self.loader = DeckLoader(self.cod_path)
        self.instructions = self.loader.instructions

        if not self.instructions:
            raise ValueError("No instructions found in the loaded file.")

        self.board = Battlefield()
        self.engine = GameEngine(self.board)

        self.current_step = 0
        self.history = []
        self.loaded = True

    # ----------
    # Next step
    # ----------
    def next_step(self):
        """Executes the next instruction in the program sequence."""
        
        # Pylance Fix: Ensure engine and board are properly initialized
        if not self.loaded or self.engine is None or self.board is None:
            raise RuntimeError("Engine not ready. Call load() first.")

        if self.current_step >= len(self.instructions):
            return {
                "done": True,
                "message": "Program finished",
                "board": self._snapshot()
            }

        inst = self.instructions[self.current_step]

        # Pylance Fix: Safely retrieve and validate the card name string
        card_name = inst.get("card")
        if not isinstance(card_name, str):
            return {"error": "Invalid or missing 'card' key in instructions."}
            
        # Pylance Fix: Ensure annotation is strictly a string
        annotation = str(inst.get("annotation", ""))

        card = factory.create(card_name)

        if not card:
            return {"error": f"Card not found in registry: {card_name}"}

        # The engine exists (checked above), so we can safely resolve
        log = self.engine.resolve(card, annotation)

        result = {
            "step": self.current_step,
            "card": card_name,
            "type": card.type,
            "annotation": annotation,
            "log": log,
            "board": self._snapshot(),
            "done": self.current_step + 1 >= len(self.instructions)
        }

        self.history.append(result)
        self.current_step += 1

        return result

    # ----------
    # Auto play
    # ----------
    def auto_play(self):
        """Executes all remaining instructions sequentially."""
        if not self.loaded:
            raise RuntimeError("Engine not ready. Call load() first.")

        results = []

        while not self.is_done():
            results.append(self.next_step())

        return results

    # ----------
    # Helpers
    # ----------
    def is_done(self):
        """Checks if the end of the instruction sequence is reached."""
        return self.current_step >= len(self.instructions)

    def reset(self):
        """Reloads the simulation from the beginning."""
        self.load()

    def get_total_steps(self):
        """Returns the total number of instructions to execute."""
        return len(self.instructions)

    def _snapshot(self):
        """Creates a snapshot of the current board state for the GUI."""
        
        # Pylance Fix: Guard against uninitialized board
        if self.board is None:
            return [[], []]
            
        grid = self.board.grid

        if not grid:
            return [[], []]

        result = [[], []]

        for row in [0, 1]:
            # Find all existing columns for the current row
            cols = sorted([col for (r, col) in grid.keys() if r == row])

            if not cols:
                result[row] = []
                continue

            min_col = min(cols)
            max_col = max(cols)

            # Build a linear representation spanning from the lowest to the highest index
            for col in range(min_col, max_col + 1):
                result[row].append(self.board.get_card_at(row, col))

        return result


# ----------
# Command Line Test Execution
# ----------
if __name__ == "__main__":
    game = GameController("data/test.cod")
    game.load()

    while True:
        res = game.next_step()

        if res.get("done"):
            print("\n=== END ===")
            break

        print(f"\nSTEP {res['step']}")
        print(f"Card: {res['card']}")
        print(f"Effect: {res.get('log', '')}")
        print(f"Board: {res['board']}")