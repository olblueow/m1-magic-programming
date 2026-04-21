from loader import DeckLoader
from battlefield import Battlefield
from engine import GameEngine
import cards.factory as factory
import copy


class GameController:
    def __init__(self, cod_path):
        self.cod_path = cod_path

        # Core
        self.loader = None
        self.instructions = []

        self.board = None
        self.engine = None

        # State
        self.current_step = 0
        self.history = []
        self.loaded = False

    # ----------
    # Load game
    # ----------
    def load(self):
        self.loader = DeckLoader(self.cod_path)
        self.instructions = self.loader.instructions

        if not self.instructions:
            raise ValueError("No instructions found")

        self.board = Battlefield()
        self.engine = GameEngine(self.board)

        self.current_step = 0
        self.history = []
        self.loaded = True

    # ----------
    # Next step
    # ----------
    def next_step(self):
        if not self.loaded:
            raise RuntimeError("Call load() first")

        if self.current_step >= len(self.instructions):
            return {
                "done": True,
                "message": "Program finished",
                "board": self._snapshot()
            }

        inst = self.instructions[self.current_step]

        card_name = inst.get("card")
        annotation = inst.get("annotation", "")

        card = factory.create(card_name)

        if not card:
            return {"error": f"Card not found: {card_name}"}

        log = self.engine.resolve(card, annotation)

        result = {
            "step": self.current_step,
            "card": card_name,
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
        if not self.loaded:
            raise RuntimeError("Call load() first")

        results = []

        while not self.is_done():
            results.append(self.next_step())

        return results

    # ----------
    # Helpers
    # ----------
    def is_done(self):
        return self.current_step >= len(self.instructions)

    def reset(self):
        self.load()

    def get_total_steps(self):
        return len(self.instructions)

    def _snapshot(self):
        grid = self.board.grid

        if not grid:
            return [[], []]

        result = [[], []]

        for row in [0, 1]:
            # to find all columns in the row
            cols = sorted([col for (r, col) in grid.keys() if r == row])

            if not cols:
                result[row] = []
                continue

            min_col = min(cols)
            max_col = max(cols)

            for col in range(min_col, max_col + 1):
                result[row].append(self.board.get_card_at(row, col))

        return result


# ----------
# Test
# ----------
if __name__ == "__main__":
    game = GameController("data/test.cod")
    game.load()

    while True:
        result = game.next_step()

        if result.get("done"):
            print("\n=== END ===")
            break

        print(f"\nSTEP {result['step']}")
        print(f"Card: {result['card']}")
        print(f"Effect: {result['log']}")
        print(f"Board: {result['board']}")